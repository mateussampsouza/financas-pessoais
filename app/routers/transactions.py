from datetime import datetime, time
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Category, Transaction
from app.schemas import TransactionCreate, TransactionUpdate, TransactionResponse

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

@router.get("", response_model=List[TransactionResponse])
def get_transactions(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    type: Optional[str] = Query(None, description="Filter by type: 'despesa', 'receita', or 'all'"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction).options(joinedload(Transaction.category))

    if start_date:
        try:
            s_date = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Transaction.date_time >= datetime.combine(s_date, time.min))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

    if end_date:
        try:
            e_date = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Transaction.date_time <= datetime.combine(e_date, time.max))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

    if type and type.lower() in ["despesa", "receita"]:
        query = query.filter(Transaction.type == type.lower())

    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    # Sort descending by date_time
    transactions = query.order_by(Transaction.date_time.desc(), Transaction.id.desc()).all()
    return transactions

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == payload.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    transaction = Transaction(
        description=payload.description.strip(),
        type=payload.type,
        amount=payload.amount,
        category_id=payload.category_id,
        date_time=payload.date_time,
        repeat_monthly=payload.repeat_monthly
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).options(joinedload(Transaction.category)).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if payload.category_id is not None:
        category = db.query(Category).filter(Category.id == payload.category_id).first()
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
    if payload.repeat_monthly is not None:
        tx.repeat_monthly = payload.repeat_monthly

    db.commit()
    db.refresh(tx)
    # Eager load category for response
    return db.query(Transaction).options(joinedload(Transaction.category)).filter(Transaction.id == transaction_id).first()

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(tx)
    db.commit()
    return None
