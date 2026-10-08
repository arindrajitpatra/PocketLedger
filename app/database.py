from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings
from app.logger import logger

db_url = settings.DATABASE_URL

# Normalize database driver URL for PostgreSQL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif db_url.startswith("postgresql://") and "+psycopg" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db() -> None:
    """
    Explicit database table creation.
    Called during application startup or CLI scripts, avoiding side effects during module import.
    """
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session for each HTTP request
    and guarantees proper session closure upon completion or error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection() -> bool:
    """
    Verify database connectivity for readiness checks.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database readiness check failed: {e}")
        return False
