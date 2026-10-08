from datetime import UTC, date, datetime

from sqlalchemy import Column, Date, DateTime, Index, Integer, Numeric, String

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), nullable=True, index=True, default="default_user")  # Ownership hook for auth
    type = Column(String(10), nullable=False, index=True)  # 'income' or 'expense'
    amount = Column(Numeric(12, 2), nullable=False)        # Precise currency storage using Decimal
    category = Column(String(50), nullable=False, index=True)
    date = Column(Date, nullable=False, default=date.today, index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    __table_args__ = (
        Index("idx_transactions_date_category", "date", "category"),
        Index("idx_transactions_type_date", "type", "date"),
    )
