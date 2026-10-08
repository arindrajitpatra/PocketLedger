from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True, default="default_user")  # Ownership hook for auth
    type: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # 'income' or 'expense'
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)        # Precise currency storage using Decimal
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date: Mapped[date] = mapped_column(nullable=False, default=date.today, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    __table_args__ = (
        Index("idx_transactions_date_category", "date", "category"),
        Index("idx_transactions_type_date", "type", "date"),
    )

