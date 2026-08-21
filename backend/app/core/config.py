from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    #
    # Environment
    #
    ENVIRONMENT: str = "development"

    #
    # Database
    #
    DATABASE_URL: str

    #
    # Legacy/default LLM configuration
    #
    LLM_API: str
    LLM_API_KEY: str

    #
    # Authentication
    #
    SECRET_KEY: str

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    #
    # CORS
    #
    CORS_ORIGINS: str = (
        "http://localhost:3000"
    )

    #
    # Paths
    #
    BASE_DIR: Path = (
        Path(__file__)
        .resolve()
        .parent
        .parent
        .parent
    )

    STORAGE_PATH: str = str(
        BASE_DIR / "storage"
    )

    DOCUMENT_STORAGE_PATH: str = (
        "./storage"
    )

    #
    # Document processing
    #
    CHUNK_SIZE: int = 1000

    CHUNK_OVERLAP: int = 200

    #
    # Background ingestion
    #
    INGESTION_WORKER_POLL_SECONDS: float = 2.0

    INGESTION_JOB_STALE_AFTER_SECONDS: int = 3600

    INGESTION_JOB_MAX_ATTEMPTS: int = 3

    #
    # Search
    #
    TOP_K: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive="ignore",
        extra="ignore",
    )


settings = Settings()