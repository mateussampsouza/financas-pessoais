from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# User / Auth Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)

class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: str = Field(..., min_length=1, max_length=50)
    color: str = Field(..., min_length=1, max_length=20)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    icon: str | None = Field(None, min_length=1, max_length=50)
    color: str | None = Field(None, min_length=1, max_length=20)

class CategoryResponse(CategoryBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class CategoryWithExpense(CategoryResponse):
    total_expense: float = 0.0
    total_income: float = 0.0

# Transaction Schemas
class TransactionBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    type: Literal["despesa", "receita"]
    amount: float = Field(..., gt=0)
    category_id: int
    date_time: datetime
    repeat_monthly: bool = False

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    description: str | None = Field(None, min_length=1, max_length=255)
    type: Literal["despesa", "receita"] | None = None
    amount: float | None = Field(None, gt=0)
    category_id: int | None = None
    date_time: datetime | None = None
    repeat_monthly: bool | None = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    category: CategoryResponse
    model_config = ConfigDict(from_attributes=True)

# Summary Schemas
class SummaryResponse(BaseModel):
    current_balance: float
    total_income: float
    total_expense: float
    recent_transactions: list[TransactionResponse]
