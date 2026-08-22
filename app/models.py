import enum
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class TransactionType(str, enum.Enum):
    DESPESA = "despesa"
    RECEITA = "receita"

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    icon = Column(String(50), nullable=False, default="tag")
    color = Column(String(20), nullable=False, default="#6366f1")

    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)  # "despesa" or "receita"
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    date_time = Column(DateTime, nullable=False)
    repeat_monthly = Column(Boolean, default=False, nullable=False)

    category = relationship("Category", back_populates="transactions")
