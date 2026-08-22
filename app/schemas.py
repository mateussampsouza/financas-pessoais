from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: str = Field(..., min_length=1, max_length=50)
    color: str = Field(..., min_length=1, max_length=20)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, min_length=1, max_length=20)

class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CategoryWithExpense(CategoryResponse):
    total_expense: float = 0.0

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
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[Literal["despesa", "receita"]] = None
    amount: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    date_time: Optional[datetime] = None
    repeat_monthly: Optional[bool] = None

class TransactionResponse(TransactionBase):
    id: int
    category: CategoryResponse
    model_config = ConfigDict(from_attributes=True)

# Summary Schemas
class SummaryResponse(BaseModel):
    current_balance: float
    total_income: float
    total_expense: float
    recent_transactions: list[TransactionResponse]
