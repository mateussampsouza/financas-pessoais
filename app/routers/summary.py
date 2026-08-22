from datetime import datetime, timedelta, time
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.database import get_db
from app.models import Transaction, User
from app.schemas import SummaryResponse, TransactionResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/summary", tags=["Summary"])

@router.get("", response_model=SummaryResponse)
def get_summary(
    base_date: Optional[str] = Query(None, description="Current reference date YYYY-MM-DD (defaults to today)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Overall balance calculation, scoped to the authenticated user
    income_sum = db.query(func.sum(Transaction.amount)).filter(
        Transaction.type == "receita", Transaction.user_id == current_user.id
    ).scalar() or 0.0
    expense_sum = db.query(func.sum(Transaction.amount)).filter(
        Transaction.type == "despesa", Transaction.user_id == current_user.id
    ).scalar() or 0.0
    balance = income_sum - expense_sum

    # Reference date for recent transactions (today and up to 3 days ago: 4 days total window)
    if base_date:
        try:
            ref_date = datetime.strptime(base_date, "%Y-%m-%d").date()
        except ValueError:
            ref_date = datetime.now().date()
    else:
        ref_date = datetime.now().date()

    start_recent = datetime.combine(ref_date - timedelta(days=3), time.min)
    end_recent = datetime.combine(ref_date, time.max)

    recent_txs = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.date_time >= start_recent,
            Transaction.date_time <= end_recent
        )
        .order_by(Transaction.date_time.desc(), Transaction.id.desc())
        .all()
    )

    return SummaryResponse(
        current_balance=round(balance, 2),
        total_income=round(income_sum, 2),
        total_expense=round(expense_sum, 2),
        recent_transactions=recent_txs
    )
