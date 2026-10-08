
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import SummaryResponse
from app.services import currency_service, summary_service

router = APIRouter(prefix="/api", tags=["Summary"])

MONTH_PATTERN = r"^(19|20)\d\d-(0[1-9]|1[0-2])$"

@router.get("/summary", response_model=SummaryResponse)
def get_monthly_summary(
    month: str | None = Query(None, pattern=MONTH_PATTERN, description="Month in YYYY-MM format (01-12)"),
    currency: str = Query("INR", description="Currency code (INR, USD, EUR, GBP)"),
    db: Session = Depends(get_db)
) -> SummaryResponse:
    """
    Get monthly financial summary including total income, total expenses,
    remaining balance, and category spending breakdowns.
    """
    if not currency_service.is_supported_currency(currency):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported currency '{currency}'. Supported: {list(currency_service.SUPPORTED_CURRENCIES.keys())}"
        )

    try:
        transactions = crud.get_all_matching_transactions(db, month=month)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )

    return summary_service.calculate_monthly_summary(
        transactions=transactions,
        month=month,
        currency=currency.upper()
    )
