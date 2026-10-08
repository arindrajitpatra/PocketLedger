"""
CRUD Database Operations

Ownership Design Note:
Multi-user authorization is planned for future lessons. Currently, all operations scope
to 'default_user' as an intentional precursor to authentication.
"""

from datetime import date as date_type, datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import extract, func, or_
from app.models import Transaction
from app.schemas import TransactionCreate, TransactionUpdate
from app.logger import logger

def validate_month_string(month_str: str) -> Tuple[int, int]:
    """Validate and parse YYYY-MM month string."""
    try:
        parts = month_str.split("-")
        if len(parts) != 2:
            raise ValueError
        year = int(parts[0])
        month_num = int(parts[1])
        if month_num < 1 or month_num > 12:
            raise ValueError
        return year, month_num
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid month value '{month_str}'. Must be in YYYY-MM format with month between 01 and 12.")

def create_transaction(db: Session, tx_data: TransactionCreate, user_id: str = "default_user") -> Transaction:
    """Create a new transaction record with automatic rollback on error."""
    db_tx = Transaction(
        user_id=user_id,
        type=tx_data.type,
        amount=tx_data.amount,
        category=tx_data.category,
        date=tx_data.date,
        description=tx_data.description
    )
    try:
        db.add(db_tx)
        db.commit()
        db.refresh(db_tx)
        logger.info(f"Created transaction ID {db_tx.id} (type: {db_tx.type}, category: {db_tx.category})")
        return db_tx
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during transaction creation: {e}")
        raise

def get_transaction_by_id(db: Session, tx_id: int, user_id: str = "default_user") -> Optional[Transaction]:
    """Fetch single transaction by ID and user ownership."""
    return db.query(Transaction).filter(
        Transaction.id == tx_id,
        Transaction.user_id == user_id
    ).first()

def get_filtered_transactions_query(
    db: Session,
    user_id: str = "default_user",
    month: Optional[str] = None,
    category: Optional[str] = None,
    tx_type: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Build reusable SQLAlchemy query for filtering transactions.
    """
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    if month:
        year, month_num = validate_month_string(month)
        query = query.filter(
            extract("year", Transaction.date) == year,
            extract("month", Transaction.date) == month_num
        )

    if category and category.lower() != "all":
        query = query.filter(func.lower(Transaction.category) == category.strip().lower())

    if tx_type and tx_type.lower() != "all":
        query = query.filter(Transaction.type == tx_type.strip().lower())

    if search:
        search_pattern = f"%{search.strip()[:100]}%"
        query = query.filter(
            or_(
                Transaction.description.ilike(search_pattern),
                Transaction.category.ilike(search_pattern)
            )
        )

    return query

def get_paginated_transactions(
    db: Session,
    user_id: str = "default_user",
    month: Optional[str] = None,
    category: Optional[str] = None,
    tx_type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20
) -> Tuple[List[Transaction], int]:
    """Fetch paginated transactions and total count."""
    query = get_filtered_transactions_query(
        db=db,
        user_id=user_id,
        month=month,
        category=category,
        tx_type=tx_type,
        search=search
    )

    total = query.count()
    offset = (page - 1) * limit
    items = query.order_by(Transaction.date.desc(), Transaction.id.desc()).offset(offset).limit(limit).all()
    
    return items, total

def get_all_matching_transactions(
    db: Session,
    user_id: str = "default_user",
    month: Optional[str] = None,
    category: Optional[str] = None,
    tx_type: Optional[str] = None,
    search: Optional[str] = None
) -> List[Transaction]:
    """Fetch all matching transactions without pagination."""
    query = get_filtered_transactions_query(
        db=db,
        user_id=user_id,
        month=month,
        category=category,
        tx_type=tx_type,
        search=search
    )
    return query.order_by(Transaction.date.desc(), Transaction.id.desc()).all()

def update_transaction(
    db: Session,
    tx_id: int,
    tx_data: TransactionUpdate,
    user_id: str = "default_user"
) -> Optional[Transaction]:
    """
    Update existing transaction.
    Supports clearing nullable fields (such as description) when explicitly supplied as null.
    """
    db_tx = get_transaction_by_id(db, tx_id, user_id=user_id)
    if not db_tx:
        return None

    update_dict = tx_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_tx, key, value)

    db_tx.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
        db.refresh(db_tx)
        logger.info(f"Updated transaction ID {tx_id}")
        return db_tx
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during transaction update (ID {tx_id}): {e}")
        raise

def delete_transaction(db: Session, tx_id: int, user_id: str = "default_user") -> bool:
    """Delete transaction with automatic rollback on failure."""
    db_tx = get_transaction_by_id(db, tx_id, user_id=user_id)
    if not db_tx:
        return False
    try:
        db.delete(db_tx)
        db.commit()
        logger.info(f"Deleted transaction ID {tx_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during transaction deletion (ID {tx_id}): {e}")
        raise

def seed_sample_data(db: Session, user_id: str = "default_user") -> List[Transaction]:
    """Development helper script to seed sample data."""
    sample_items = [
        {"type": "income", "amount": Decimal("50000.00"), "category": "Salary", "date": date_type.today(), "description": "Monthly Salary"},
        {"type": "expense", "amount": Decimal("15000.00"), "category": "Rent", "date": date_type.today(), "description": "Apartment Rent"},
        {"type": "expense", "amount": Decimal("4500.00"), "category": "Food", "date": date_type.today(), "description": "Groceries & Dining"},
        {"type": "expense", "amount": Decimal("2000.00"), "category": "Transport", "date": date_type.today(), "description": "Fuel & Metro"},
        {"type": "expense", "amount": Decimal("1200.00"), "category": "Bills", "date": date_type.today(), "description": "Electricity & Water"},
        {"type": "expense", "amount": Decimal("3500.00"), "category": "Shopping", "date": date_type.today(), "description": "Clothing & Essentials"},
        {"type": "income", "amount": Decimal("8000.00"), "category": "Freelance", "date": date_type.today(), "description": "Web Design Project"},
    ]
    created = []
    try:
        for item in sample_items:
            tx = Transaction(user_id=user_id, **item)
            db.add(tx)
            created.append(tx)
        db.commit()
        return created
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding sample data: {e}")
        raise
