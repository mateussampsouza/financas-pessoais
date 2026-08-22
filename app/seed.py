from sqlalchemy.orm import Session
from app.models import Category

DEFAULT_CATEGORIES = [
    {"name": "Alimentação", "icon": "utensils", "color": "#ef4444"},
    {"name": "Transporte", "icon": "car", "color": "#f97316"},
    {"name": "Moradia", "icon": "home", "color": "#eab308"},
    {"name": "Lazer", "icon": "gamepad-2", "color": "#8b5cf6"},
    {"name": "Salário", "icon": "wallet", "color": "#10b981"},
    {"name": "Investimentos", "icon": "trending-up", "color": "#06b6d4"},
    {"name": "Saúde", "icon": "heart-pulse", "color": "#ec4899"},
    {"name": "Educação", "icon": "graduation-cap", "color": "#3b82f6"},
    {"name": "Outros", "icon": "tag", "color": "#64748b"},
]

def seed_default_categories(db: Session, user_id: int):
    """Create the default category set for a newly registered user.
    Safe to call more than once: it's a no-op if the user already has categories."""
    count = db.query(Category).filter(Category.user_id == user_id).count()
    if count == 0:
        for cat in DEFAULT_CATEGORIES:
            category = Category(name=cat["name"], icon=cat["icon"], color=cat["color"], user_id=user_id)
            db.add(category)
        db.commit()
