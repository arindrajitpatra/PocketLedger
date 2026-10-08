import datetime as dt
from decimal import Decimal

from sqlalchemy import Date, DateTime, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True, default="default_user")  # Ownership hook for auth
    type: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # 'income' or 'expense'
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)        # Precise currency storage using Decimal
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date: Mapped[dt.date] = mapped_column(Date, nullable=False, default=dt.date.today, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC))
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC), onupdate=lambda: dt.datetime.now(dt.UTC))

    __table_args__ = (
        Index("idx_transactions_date_category", "date", "category"),
        Index("idx_transactions_type_date", "type", "date"),
    )


