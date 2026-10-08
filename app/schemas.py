from datetime import date as date_type, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict

ALLOWED_TRANSACTION_TYPES = {"income", "expense"}

class TransactionBase(BaseModel):
    type: str = Field(..., description="Transaction type: 'income' or 'expense'")
    amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=12, description="Monetary amount (greater than 0)")
    category: str = Field(..., min_length=1, max_length=50, description="Category name (non-empty)")
    date: date_type = Field(..., description="Transaction date (YYYY-MM-DD)")
    description: Optional[str] = Field(None, max_length=255, description="Optional description (max 255 chars)")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        v_clean = v.lower().strip()
        if v_clean not in ALLOWED_TRANSACTION_TYPES:
            raise ValueError("Type must be either 'income' or 'expense'")
        return v_clean

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("Category cannot be empty or whitespace only")
        return v_clean

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= Decimal("0.00"):
            raise ValueError("Amount must be greater than zero")
        return round(v, 2)

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    type: Optional[str] = None
    amount: Optional[Decimal] = None
    category: Optional[str] = None
    date: Optional[date_type] = None
    description: Optional[str] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_clean = v.lower().strip()
        if v_clean not in ALLOWED_TRANSACTION_TYPES:
            raise ValueError("Type must be either 'income' or 'expense'")
        return v_clean

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("Category cannot be empty or whitespace only")
        return v_clean

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None:
            if v <= Decimal("0.00"):
                raise ValueError("Amount must be greater than zero")
            return round(v, 2)
        return v

class TransactionResponse(TransactionBase):
    id: int
    user_id: Optional[str] = "default_user"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedTransactionResponse(BaseModel):
    items: List[TransactionResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class CategoryBreakdown(BaseModel):
    category: str
    amount: Decimal
    percentage: float

class SummaryResponse(BaseModel):
    month: Optional[str] = None  # YYYY-MM or None for all-time
    currency: str = "INR"
    total_income: Decimal
    total_expenses: Decimal
    remaining_balance: Decimal
    category_breakdown: List[CategoryBreakdown]
    expense_category_breakdown: List[CategoryBreakdown]
    income_category_breakdown: List[CategoryBreakdown]
    transaction_count: int

class HealthResponse(BaseModel):
    status: str
    app: str
    version: str

class ReadyResponse(BaseModel):
    status: str
    database: str

class SeedResponse(BaseModel):
    message: str
    count: int
