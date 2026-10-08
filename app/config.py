import os
from typing import Set
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

VALID_ENVS: Set[str] = {"development", "testing", "production", "staging"}
VALID_LOG_LEVELS: Set[str] = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

class Settings:
    """
    Application configuration with safe defaults for local development
    and explicit validation for environment variables.
    """
    APP_NAME: str = os.getenv("APP_NAME", "PocketLedger")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    APP_ENV: str = os.getenv("APP_ENV", "development").lower()
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pocketledger.db")

    def __init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.APP_ENV not in VALID_ENVS:
            raise ValueError(
                f"Invalid APP_ENV '{self.APP_ENV}'. Allowed values: {VALID_ENVS}"
            )
        if self.LOG_LEVEL not in VALID_LOG_LEVELS:
            raise ValueError(
                f"Invalid LOG_LEVEL '{self.LOG_LEVEL}'. Allowed values: {VALID_LOG_LEVELS}"
            )
        if not self.DATABASE_URL or not self.DATABASE_URL.strip():
            raise ValueError("DATABASE_URL must be specified and non-empty.")

settings = Settings()
