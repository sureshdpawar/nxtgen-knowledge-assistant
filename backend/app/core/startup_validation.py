import logging

from pathlib import Path

from app.core.config import settings


logger = logging.getLogger(
    "nxtgen.startup"
)


MIN_SECRET_KEY_LENGTH = 32


def validate_startup_configuration() -> None:
    errors: list[str] = []

    warnings: list[str] = []


    #
    # Environment
    #
    environment = (
        settings.ENVIRONMENT
        .strip()
        .lower()
    )

    allowed_environments = {
        "development",
        "test",
        "production",
    }

    if (
        environment
        not in allowed_environments
    ):
        errors.append(
            "ENVIRONMENT must be one of: "
            "development, test, production."
        )


    #
    # Database
    #
    if not settings.DATABASE_URL.strip():
        errors.append(
            "DATABASE_URL is missing."
        )


    #
    # JWT secret
    #
    secret_key = (
        settings.SECRET_KEY.strip()
    )

    if not secret_key:
        errors.append(
            "SECRET_KEY is missing."
        )

    elif (
        len(secret_key)
        < MIN_SECRET_KEY_LENGTH
    ):
        errors.append(
            "SECRET_KEY must be at least "
            "32 characters long."
        )


    #
    # JWT algorithm
    #
    if not settings.ALGORITHM.strip():
        errors.append(
            "ALGORITHM is missing."
        )


    #
    # Document storage
    #
    storage_path = Path(
        settings.DOCUMENT_STORAGE_PATH
    )

    try:
        storage_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    except OSError as exc:
        errors.append(
            "DOCUMENT_STORAGE_PATH "
            "cannot be created: "
            f"{exc}"
        )

    else:
        if not storage_path.is_dir():
            errors.append(
                "DOCUMENT_STORAGE_PATH "
                "is not a directory."
            )


    #
    # Chunk configuration
    #
    if settings.CHUNK_SIZE <= 0:
        errors.append(
            "CHUNK_SIZE must be "
            "greater than zero."
        )

    if settings.CHUNK_OVERLAP < 0:
        errors.append(
            "CHUNK_OVERLAP cannot "
            "be negative."
        )

    if (
        settings.CHUNK_OVERLAP
        >= settings.CHUNK_SIZE
    ):
        errors.append(
            "CHUNK_OVERLAP must be "
            "smaller than CHUNK_SIZE."
        )


    #
    # Search configuration
    #
    if settings.TOP_K <= 0:
        errors.append(
            "TOP_K must be "
            "greater than zero."
        )


    #
    # CORS
    #
    cors_origins = [
        origin.strip()
        for origin
        in settings.CORS_ORIGINS.split(",")
        if origin.strip()
    ]

    if not cors_origins:
        errors.append(
            "CORS_ORIGINS must contain "
            "at least one origin."
        )

    if (
        environment == "production"
        and "*" in cors_origins
    ):
        errors.append(
            "CORS_ORIGINS cannot contain "
            "'*' in production."
        )


    #
    # Development warnings
    #
    if (
        environment != "production"
        and "*" in cors_origins
    ):
        warnings.append(
            "CORS allows all origins."
        )


    #
    # Log warnings
    #
    for warning in warnings:
        logger.warning(
            "Startup configuration warning: %s",
            warning,
        )


    #
    # Fail startup
    #
    if errors:
        formatted_errors = "\n".join(
            f"- {error}"
            for error in errors
        )

        raise RuntimeError(
            "Startup configuration "
            "validation failed:\n"
            f"{formatted_errors}"
        )


    logger.info(
        "Startup configuration validated "
        "environment=%s",
        environment,
    )