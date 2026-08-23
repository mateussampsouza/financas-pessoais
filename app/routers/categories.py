from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Category, Transaction, User
from app.schemas import CategoryCreate, CategoryResponse, CategoryUpdate, CategoryWithExpense

router = APIRouter(prefix="/api/categories", tags=["Categories"])

@router.get("", response_model=list[CategoryWithExpense])
def get_categories(
    start_date: str | None = Query(None, description="Start date YYYY-MM-DD"),
    end_date: str | None = Query(None, description="End date YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    categories = db.query(Category).filter(Category.user_id == current_user.id).order_by(Category.name).all()

    # Query total per type (despesa/receita) per category in the specified period, scoped to this user
    totals_query = db.query(
        Transaction.category_id,
        Transaction.type,
        func.sum(Transaction.amount).label("total")
    ).filter(Transaction.user_id == current_user.id)

    if start_date:
        try:
            s_date = datetime.strptime(start_date, "%Y-%m-%d")
            totals_query = totals_query.filter(Transaction.date_time >= datetime.combine(s_date, time.min))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD") from None

    if end_date:
        try:
            e_date = datetime.strptime(end_date, "%Y-%m-%d")
            totals_query = totals_query.filter(Transaction.date_time <= datetime.combine(e_date, time.max))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD") from None

    expense_map = {}
    income_map = {}
    for category_id, tx_type, total in totals_query.group_by(Transaction.category_id, Transaction.type).all():
        if tx_type == "despesa":
            expense_map[category_id] = total
        else:
            income_map[category_id] = total

    result = []
    for cat in categories:
        result.append(
            CategoryWithExpense(
                id=cat.id,
                user_id=cat.user_id,
                name=cat.name,
                icon=cat.icon,
                color=cat.color,
                total_expense=float(expense_map.get(cat.id, 0.0) or 0.0),
                total_income=float(income_map.get(cat.id, 0.0) or 0.0)
            )
        )
    return result

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(Category).filter(
        Category.user_id == current_user.id,
        func.lower(Category.name) == func.lower(payload.name)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")

    category = Category(
        name=payload.name.strip(),
        icon=payload.icon.strip(),
        color=payload.color.strip(),
        user_id=current_user.id
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cat = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cat = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    if payload.name is not None:
        name_clean = payload.name.strip()
        existing = db.query(Category).filter(
            Category.user_id == current_user.id,
            func.lower(Category.name) == func.lower(name_clean),
            Category.id != category_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        cat.name = name_clean

    if payload.icon is not None:
        cat.icon = payload.icon.strip()
    if payload.color is not None:
        cat.color = payload.color.strip()

    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cat = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    # Block deletion if this category has transactions linked to it
    tx_count = db.query(Transaction).filter(
        Transaction.category_id == category_id,
        Transaction.user_id == current_user.id
    ).count()
    if tx_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir uma categoria que possui transações vinculadas."
        )

    db.delete(cat)
    db.commit()
    return None
