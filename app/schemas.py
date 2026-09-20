from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    """Whether a transaction represents money coming in or going out."""
    INCOME = "income"
    EXPENSE = "expense"


class TransactionBase(BaseModel):
    """
    Fields shared by all transaction schemas.

    This base class exists so we don't repeat field definitions across
    the "create" and "read" schemas below (DRY principle).
    """
    date: date
    merchant: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    transaction_type: TransactionType


class TransactionCreate(TransactionBase):
    """
    Schema for creating a new transaction via the API.

    Deliberately does NOT include 'id' or 'category' — the server
    generates the id, and Stage 5 will auto-assign the category.
    The client shouldn't be able to set either of these itself.
    """
    pass


class TransactionRead(TransactionBase):
    """
    Schema for returning a transaction to the client.

    Includes fields the server assigns: id and category.
    """
    id: UUID = Field(default_factory=uuid4)
    category: str

    class Config:
        from_attributes = True  # allows creation from SQLAlchemy model objects, not just dicts