import logging

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db


logger = logging.getLogger(
    "nxtgen.health"
)


router = APIRouter(
    tags=["Health"],
)


@router.get(
    "/health",
)
def health() -> dict:
    return {
        "status": "ok",
    }


@router.get(
    "/ready",
)
def readiness(
    response: Response,
    db: Session = Depends(
        get_db,
    ),
) -> dict:
    try:
        db.execute(
            text("SELECT 1")
        )

        return {
            "status": "ready",
            "database": "ok",
        }

    except Exception:
        logger.exception(
            "Readiness check failed"
        )

        response.status_code = (
            status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return {
            "status": "not_ready",
            "database": "unavailable",
        }