from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

RecurrenceType = Literal["nunca", "diaria", "semanal", "mensal", "anual"]


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

class TransactionCreate(TransactionBase):
    recurrence: RecurrenceType = "nunca"
    recurrence_quantity: int | None = Field(None, ge=1, le=99)
    recurrence_installment: int | None = Field(None, ge=1, le=99)

    @model_validator(mode="after")
    def validate_recurrence(self):
        if self.recurrence == "nunca":
            self.recurrence_quantity = None
            self.recurrence_installment = None
        else:
            if self.recurrence_quantity is None or self.recurrence_installment is None:
                raise ValueError("recurrence_quantity e recurrence_installment são obrigatórios quando recurrence não é 'nunca'")
            if self.recurrence_installment > self.recurrence_quantity:
                raise ValueError("recurrence_installment não pode ser maior que recurrence_quantity")
        return self

# recurrence, recurrence_quantity and recurrence_installment are intentionally
# absent here: they're immutable after creation (locked in the UI too).
class TransactionUpdate(BaseModel):
    description: str | None = Field(None, min_length=1, max_length=255)
    type: Literal["despesa", "receita"] | None = None
    amount: float | None = Field(None, gt=0)
    category_id: int | None = None
    date_time: datetime | None = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    recurrence: RecurrenceType
    recurrence_quantity: int | None
    recurrence_installment: int | None
    recurrence_group_id: str | None
    category: CategoryResponse
    model_config = ConfigDict(from_attributes=True)

# Summary Schemas
class SummaryResponse(BaseModel):
    current_balance: float
    total_income: float
    total_expense: float
    recent_transactions: list[TransactionResponse]
