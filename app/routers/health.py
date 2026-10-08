from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.database import check_db_connection
from app.schemas import HealthResponse, ReadyResponse

router = APIRouter(tags=["Health & Readiness"])

@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Liveness probe: verifies that the application process is running."""
    return HealthResponse(
        status="ok",
        app=settings.APP_NAME,
        version=settings.APP_VERSION
    )

@router.get("/ready", response_model=ReadyResponse)
def readiness_check() -> ReadyResponse:
    """Readiness probe: verifies database connectivity and operational readiness."""
    db_ok = check_db_connection()
    if not db_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connectivity check failed"
        )
    return ReadyResponse(
        status="ready",
        database="connected"
    )
