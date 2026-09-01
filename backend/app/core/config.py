from pathlib import Path
from typing import Literal

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
    # Google Drive
    #
    GOOGLE_SERVICE_ACCOUNT_FILE: (
        str | None
    ) = None

    #
    # Document processing
    #
    CHUNK_SIZE: int = 1000

    CHUNK_OVERLAP: int = 200

    #
    # Background ingestion
    #
    INGESTION_WORKER_POLL_SECONDS: (
        float
    ) = 2.0

    INGESTION_JOB_STALE_AFTER_SECONDS: (
        int
    ) = 3600

    INGESTION_JOB_MAX_ATTEMPTS: (
        int
    ) = 3

    #
    # Retrieval
    #
    # Final number of chunks returned by
    # retrieval and supplied to generation.
    #
    TOP_K: int = 5

    #
    # Embedding model used for document
    # and query embeddings.
    #
    EMBEDDING_MODEL: str = (
        "BAAI/bge-small-en-v1.5"
    )

    #
    # Vector dimensionality produced by
    # EMBEDDING_MODEL.
    #
    # Changing this value may require a
    # pgvector schema migration as well as
    # re-embedding all persisted content.
    #
    EMBEDDING_DIMENSIONS: int = 384

    #
    # Cross-encoder reranker used after
    # broad vector candidate retrieval.
    #
    RERANKER_MODEL: str = (
        "mixedbread-ai/"
        "mxbai-rerank-base-v1"
    )

    #
    # Candidate retrieval policy.
    #
    # Example:
    #
    # final_top_k = 5
    # multiplier = 3
    # candidate_top_k = 15
    #
    RERANKER_CANDIDATE_MULTIPLIER: (
        int
    ) = 3

    #
    # Safety cap on vector candidates sent
    # to the reranker.
    #
    RERANKER_MAX_CANDIDATES: int = 50

    #
    # Usage quota platform defaults
    #
    DEFAULT_DAILY_MESSAGE_LIMIT: (
        int
    ) = 50

    DEFAULT_DAILY_INPUT_TOKEN_LIMIT: (
        int
    ) = 50_000

    DEFAULT_DAILY_OUTPUT_TOKEN_LIMIT: (
        int
    ) = 20_000

    DEFAULT_DAILY_TOTAL_TOKEN_LIMIT: (
        int
    ) = 70_000

    DEFAULT_MONTHLY_MESSAGE_LIMIT: (
        int
    ) = 1_000

    DEFAULT_MONTHLY_INPUT_TOKEN_LIMIT: (
        int
    ) = 1_000_000

    DEFAULT_MONTHLY_OUTPUT_TOKEN_LIMIT: (
        int
    ) = 400_000

    DEFAULT_MONTHLY_TOTAL_TOKEN_LIMIT: (
        int
    ) = 1_400_000

    DEFAULT_MAX_INPUT_TOKENS_PER_REQUEST: (
        int
    ) = 8_000

    DEFAULT_MAX_OUTPUT_TOKENS_PER_REQUEST: (
        int
    ) = 2_048

    DEFAULT_USAGE_TIMEZONE: str = (
        "UTC"
    )

    #
    # Website widget authentication
    #
    WEBSITE_WIDGET_TOKEN_SECRET: str = (
        "hJBA8tg8T3Nq2JWJBWh2GEFhpw6Exu4h"
        "xXytWg77K11pq45D5MEbnjPMvZJEHTsf"
    )

    WEBSITE_WIDGET_TOKEN_TTL_MINUTES: (
        int
    ) = 30

    #
    # Online evaluation
    #
    ONLINE_EVAL_ENABLED: bool = True

    ONLINE_EVAL_SAMPLE_RATE: float = 0.05
    
    #
    # OpenTelemetry
    #
    OTEL_ENABLED: bool = True

    OTEL_SERVICE_NAME: str = (
        "knowgentiq-backend"
    )

    OTEL_TRACE_EXPORTER: Literal[
        "none",
        "console",
        "otlp",
    ] = "console"

    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT: (
        str | None
    ) = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive="ignore",
        extra="ignore",
    )


settings = Settings()