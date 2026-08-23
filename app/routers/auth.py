from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, get_password_hash, verify_password
from app.database import get_db
from app.limiter import limiter
from app.models import User
from app.schemas import Token, UserCreate, UserLogin, UserResponse
from app.seed import seed_default_categories

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    username_clean = payload.username.strip()
    existing = db.query(User).filter(func.lower(User.username) == func.lower(username_clean)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Este nome de usuário já está em uso.")

    user = User(
        username=username_clean,
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Seed default categories for the new user
    seed_default_categories(db, user.id)

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, token_type="bearer")


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.username) == func.lower(payload.username.strip())).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos.")

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
