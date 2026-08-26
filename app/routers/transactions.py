import calendar
import uuid
from datetime import datetime, time, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user
from app.database import get_db
from app.models import Category, Transaction, User
from app.schemas import TransactionCreate, TransactionResponse, TransactionUpdate

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


def _shift_months(base: datetime, months: int) -> datetime:
    total = base.month - 1 + months
    year = base.year + total // 12
    month = total % 12 + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return base.replace(year=year, month=month, day=day)


def _occurrence_date(base: datetime, recurrence: str, offset: int) -> datetime:
    """Date of the occurrence `offset` steps away from `base` (negative = past)."""
    if offset == 0:
        return base
    if recurrence == "diaria":
        return base + timedelta(days=offset)
    if recurrence == "semanal":
        return base + timedelta(weeks=offset)
    if recurrence == "mensal":
        return _shift_months(base, offset)
    if recurrence == "anual":
        return _shift_months(base, offset * 12)
    return base

@router.get("", response_model=list[TransactionResponse])
def get_transactions(
    start_date: str | None = Query(None, description="Start date YYYY-MM-DD"),
    end_date: str | None = Query(None, description="End date YYYY-MM-DD"),
    type: str | None = Query(None, description="Filter by type: 'despesa', 'receita', or 'all'"),
    category_id: int | None = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Transaction).options(joinedload(Transaction.category)).filter(Transaction.user_id == current_user.id)

    if start_date:
        try:
            s_date = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Transaction.date_time >= datetime.combine(s_date, time.min))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD") from None

    if end_date:
        try:
            e_date = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Transaction.date_time <= datetime.combine(e_date, time.max))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD") from None

    if type and type.lower() in ["despesa", "receita"]:
        query = query.filter(Transaction.type == type.lower())

    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    # Sort descending by date_time
    transactions = query.order_by(Transaction.date_time.desc(), Transaction.id.desc()).all()
    return transactions

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.query(Category).filter(Category.id == payload.category_id, Category.user_id == current_user.id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    if payload.recurrence == "nunca":
        transaction = Transaction(
            description=payload.description.strip(),
            type=payload.type,
            amount=payload.amount,
            category_id=payload.category_id,
            date_time=payload.date_time,
            recurrence="nunca",
            user_id=current_user.id
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    # Recurring series: `recurrence_installment` is this transaction's position (1-indexed)
    # within a `recurrence_quantity`-long series. Positions before it are generated into
    # the past, positions after it into the future, all sharing one recurrence_group_id.
    quantity = payload.recurrence_quantity
    installment = payload.recurrence_installment
    group_id = str(uuid.uuid4())
    created_transaction = None

    for position in range(1, quantity + 1):
        occurrence_date = _occurrence_date(payload.date_time, payload.recurrence, position - installment)
        tx = Transaction(
            description=payload.description.strip(),
            type=payload.type,
            amount=payload.amount,
            category_id=payload.category_id,
            date_time=occurrence_date,
            recurrence=payload.recurrence,
            recurrence_quantity=quantity,
            recurrence_installment=position,
            recurrence_group_id=group_id,
            user_id=current_user.id
        )
        db.add(tx)
        if position == installment:
            created_transaction = tx

    db.commit()
    db.refresh(created_transaction)
    return created_transaction

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tx = db.query(Transaction).options(joinedload(Transaction.category)).filter(
        Transaction.id == transaction_id, Transaction.user_id == current_user.id
    ).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if payload.category_id is not None:
        category = db.query(Category).filter(Category.id == payload.category_id, Category.user_id == current_user.id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
        tx.category_id = payload.category_id

    if payload.description is not None:
        tx.description = payload.description.strip()
    if payload.type is not None:
        tx.type = payload.type
    if payload.amount is not None:
        tx.amount = payload.amount
    if payload.date_time is not None:
        tx.date_time = payload.date_time

    db.commit()
    db.refresh(tx)
    # Eager load category for response
    return db.query(Transaction).options(joinedload(Transaction.category)).filter(
        Transaction.id == transaction_id, Transaction.user_id == current_user.id
    ).first()

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    mode: Literal["only", "following"] = Query("only", description="'only' deletes just this transaction; 'following' also deletes later transactions in the same recurrence series"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if mode == "following" and tx.recurrence_group_id:
        db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.recurrence_group_id == tx.recurrence_group_id,
            Transaction.date_time >= tx.date_time
        ).delete(synchronize_session=False)
    else:
        db.delete(tx)

    db.commit()
    return None
