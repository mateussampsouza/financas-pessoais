from datetime import datetime, time
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Category, Transaction
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithExpense

router = APIRouter(prefix="/api/categories", tags=["Categories"])

@router.get("", response_model=List[CategoryWithExpense])
def get_categories(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    categories = db.query(Category).order_by(Category.name).all()
    
    # Query total expenses per category in the specified period
    expense_query = db.query(
        Transaction.category_id,
        func.sum(Transaction.amount).label("total_expense")
    ).filter(Transaction.type == "despesa")

    if start_date:
        try:
            s_date = datetime.strptime(start_date, "%Y-%m-%d")
            expense_query = expense_query.filter(Transaction.date_time >= datetime.combine(s_date, time.min))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

    if end_date:
        try:
            e_date = datetime.strptime(end_date, "%Y-%m-%d")
            expense_query = expense_query.filter(Transaction.date_time <= datetime.combine(e_date, time.max))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

    expense_map = dict(expense_query.group_by(Transaction.category_id).all())

    result = []
    for cat in categories:
        total = float(expense_map.get(cat.id, 0.0) or 0.0)
        result.append(
            CategoryWithExpense(
                id=cat.id,
                name=cat.name,
                icon=cat.icon,
                color=cat.color,
                total_expense=total
            )
        )
    return result

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(func.lower(Category.name) == func.lower(payload.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    category = Category(
        name=payload.name.strip(),
        icon=payload.icon.strip(),
        color=payload.color.strip()
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    if payload.name is not None:
        name_clean = payload.name.strip()
        existing = db.query(Category).filter(
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
def delete_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check if category has transactions
    tx_count = db.query(Transaction).filter(Transaction.category_id == category_id).count()
    if tx_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível excluir esta categoria pois ela possui {tx_count} transação(ões) vinculada(s)."
        )

    db.delete(cat)
    db.commit()
    return None
