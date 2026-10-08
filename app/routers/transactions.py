import csv
import io
import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import crud
from app.config import settings
from app.database import get_db
from app.logger import logger
from app.schemas import (
    PaginatedTransactionResponse,
    SeedResponse,
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)

router = APIRouter(prefix="/api", tags=["Transactions"])

MONTH_PATTERN = r"^(19|20)\d\d-(0[1-9]|1[0-2])$"

@router.get("/transactions", response_model=PaginatedTransactionResponse)
def read_transactions(
    month: str | None = Query(None, pattern=MONTH_PATTERN, description="Format YYYY-MM (01-12)"),
    category: str | None = Query(None, max_length=50, description="Category filter"),
    type: str | None = Query(None, description="'income' or 'expense'"),
    search: str | None = Query(None, max_length=100, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
) -> PaginatedTransactionResponse:
    """
    Retrieve paginated transactions with optional filtering by month, category, type, and search query.
    """
    try:
        items, total = crud.get_paginated_transactions(
            db=db,
            month=month,
            category=category,
            tx_type=type,
            search=search,
            page=page,
            limit=limit
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )

    total_pages = math.ceil(total / limit) if total > 0 else 1

    return PaginatedTransactionResponse(
        items=[TransactionResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )

@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    tx_data: TransactionCreate,
    db: Session = Depends(get_db)
) -> TransactionResponse:
    """Create a new income or expense transaction."""
    logger.info(f"Received request to create transaction (type: {tx_data.type}, category: {tx_data.category})")
    created = crud.create_transaction(db, tx_data)
    return TransactionResponse.model_validate(created)

@router.get("/transactions/{tx_id}", response_model=TransactionResponse)
def read_transaction(tx_id: int, db: Session = Depends(get_db)) -> TransactionResponse:
    """Fetch details of a specific transaction by ID."""
    db_tx = crud.get_transaction_by_id(db, tx_id)
    if not db_tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {tx_id} not found"
        )
    return TransactionResponse.model_validate(db_tx)

@router.put("/transactions/{tx_id}", response_model=TransactionResponse)
def update_transaction(
    tx_id: int,
    tx_data: TransactionUpdate,
    db: Session = Depends(get_db)
) -> TransactionResponse:
    """Update an existing transaction. Requires at least one field to be supplied."""
    update_data = tx_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided for update."
        )

    updated_tx = crud.update_transaction(db, tx_id, tx_data)
    if not updated_tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {tx_id} not found"
        )
    return TransactionResponse.model_validate(updated_tx)

@router.delete("/transactions/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(tx_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a transaction by ID."""
    success = crud.delete_transaction(db, tx_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {tx_id} not found"
        )

@router.get("/export/csv")
def export_csv(
    month: str | None = Query(None, pattern=MONTH_PATTERN),
    category: str | None = Query(None, max_length=50),
    type: str | None = Query(None),
    search: str | None = Query(None, max_length=100),
    db: Session = Depends(get_db)
) -> StreamingResponse:
    """
    Export transactions matching exact filter criteria to downloadable CSV format.
    """
    try:
        txs = crud.get_all_matching_transactions(
            db=db,
            month=month,
            category=category,
            tx_type=type,
            search=search
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["ID", "Date", "Type", "Category", "Amount", "Description", "Created At"])

    for tx in txs:
        writer.writerow([
            tx.id,
            tx.date.strftime("%Y-%m-%d"),
            tx.type.capitalize(),
            tx.category,
            f"{tx.amount:.2f}",
            tx.description or "",
            tx.created_at.strftime("%Y-%m-%d %H:%M:%S") if tx.created_at else ""
        ])

    output.seek(0)
    filename = f"pocketledger_export_{month or 'all'}.csv"

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/seed", response_model=SeedResponse)
def seed_data(db: Session = Depends(get_db)) -> SeedResponse:
    """Development API route to explicitly seed sample data."""
    if settings.APP_ENV.lower() == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seeding sample data is disabled in production environment."
        )

    created = crud.seed_sample_data(db)
    return SeedResponse(
        message="Sample transactions created successfully",
        count=len(created)
    )
