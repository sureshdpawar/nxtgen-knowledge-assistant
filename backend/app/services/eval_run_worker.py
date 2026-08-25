import logging

from uuid import UUID

from app.db.session import SessionLocal
from app.services.eval_experiment_service import (
    EvalExperimentService,
)


logger = logging.getLogger(
    "nxtgen.eval"
)


def execute_retrieval_experiment(
    experiment_id: UUID,
) -> None:
    """Execute one persisted retrieval evaluation run.

    The API owns run creation. This worker owns execution and opens
    its own database session so it can run outside the request scope.
    The function is deliberately queue-agnostic: FastAPI background
    tasks can call it in V1 and a durable worker can call the same
    function later without changing the product/API abstraction.
    """

    db = SessionLocal()

    try:
        service = EvalExperimentService()
        service.execute_retrieval_experiment(
            db=db,
            experiment_id=experiment_id,
        )
    except Exception:
        logger.exception(
            "Evaluation run failed experiment_id=%s",
            experiment_id,
        )
    finally:
        db.close()
