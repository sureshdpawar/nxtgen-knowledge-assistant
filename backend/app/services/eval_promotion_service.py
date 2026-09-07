from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy import (
    select,
)
from sqlalchemy.exc import (
    IntegrityError,
)
from sqlalchemy.orm import Session

from app.core.enums import (
    AgentRunStatus,
)
from app.models.agent import Agent
from app.models.agent_run import AgentRun
from app.models.eval_case import EvalCase
from app.models.eval_dataset import EvalDataset
from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.models.user import User
from app.schemas.eval_promotion import (
    AgentRunEvalPromotionRequest,
)


class EvalPromotionService:

    def _get_run(
        self,
        db: Session,
        current_user: User,
        run_id: UUID,
    ) -> AgentRun:
        stmt = (
            select(
                AgentRun,
            )
            .where(
                AgentRun.id == run_id,
                AgentRun.tenant_id
                == current_user.tenant_id,
            )
        )

        run = db.scalars(
            stmt,
        ).first()

        if run is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail="Agent run not found.",
            )

        return run

    def _get_agent(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
    ) -> Agent:
        stmt = (
            select(
                Agent,
            )
            .where(
                Agent.id == agent_id,
                Agent.tenant_id
                == current_user.tenant_id,
            )
        )

        agent = db.scalars(
            stmt,
        ).first()

        if agent is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail="Agent not found.",
            )

        return agent

    def _get_dataset(
        self,
        db: Session,
        current_user: User,
        dataset_id: UUID,
    ) -> EvalDataset:
        stmt = (
            select(
                EvalDataset,
            )
            .join(
                KnowledgeBase,
                KnowledgeBase.id
                == EvalDataset.knowledge_base_id,
            )
            .where(
                EvalDataset.id == dataset_id,
                KnowledgeBase.tenant_id
                == current_user.tenant_id,
            )
        )

        dataset = db.scalars(
            stmt,
        ).first()

        if dataset is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail="Eval dataset not found.",
            )

        return dataset

    def _existing_promotion(
        self,
        db: Session,
        run_id: UUID,
    ) -> EvalCase | None:
        stmt = (
            select(
                EvalCase,
            )
            .where(
                EvalCase.source_agent_run_id
                == run_id,
            )
        )

        return db.scalars(
            stmt,
        ).first()

    def promote(
        self,
        db: Session,
        current_user: User,
        run_id: UUID,
        payload:
            AgentRunEvalPromotionRequest,
    ) -> dict:
        run = self._get_run(
            db=db,
            current_user=current_user,
            run_id=run_id,
        )

        if (
            run.status
            != AgentRunStatus.COMPLETED
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail=(
                    "Only completed agent "
                    "runs can be promoted."
                ),
            )

        answer = (
            run.answer.strip()
            if run.answer is not None
            else ""
        )

        if not answer:
            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail=(
                    "Completed agent run "
                    "does not have an answer "
                    "to promote."
                ),
            )

        existing = (
            self._existing_promotion(
                db=db,
                run_id=run.id,
            )
        )

        if existing is not None:
            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail=(
                    "Agent run has already "
                    "been promoted to an "
                    "evaluation case."
                ),
            )

        agent = self._get_agent(
            db=db,
            current_user=current_user,
            agent_id=run.agent_id,
        )

        dataset = self._get_dataset(
            db=db,
            current_user=current_user,
            dataset_id=payload.dataset_id,
        )

        if (
            dataset.knowledge_base_id
            not in agent.knowledge_base_ids
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Eval dataset Knowledge "
                    "Base is not assigned to "
                    "this agent."
                ),
            )

        tools_used = list(
            run.tools_used or []
        )

        source_metadata = {
            "agent_id":
                str(run.agent_id),
            "actor_type":
                run.actor_type,
            "tools_used":
                tools_used,
            "llm_calls":
                run.llm_calls,
            "duration_ms":
                run.duration_ms,
            "completed_at": (
                run.completed_at.isoformat()
                if run.completed_at
                is not None
                else None
            ),
            "promoted_by_user_id":
                str(current_user.id),
        }

        eval_case = EvalCase(
            dataset_id=
                dataset.id,
            question=
                run.query,
            source_agent_run_id=
                run.id,
            source_metadata=
                source_metadata,
            expected_sources=[],
            expected_answer=
                answer,
            answerable=
                payload.answerable,
        )

        db.add(
            eval_case,
        )

        try:
            db.commit()

        except IntegrityError as exc:
            db.rollback()

            existing = (
                self._existing_promotion(
                    db=db,
                    run_id=run.id,
                )
            )

            if existing is not None:
                raise HTTPException(
                    status_code=
                        status.HTTP_409_CONFLICT,
                    detail=(
                        "Agent run has already "
                        "been promoted to an "
                        "evaluation case."
                    ),
                ) from exc

            raise

        db.refresh(
            eval_case,
        )

        return {
            "eval_case_id":
                eval_case.id,
            "dataset_id":
                eval_case.dataset_id,
            "source_agent_run_id":
                run.id,
            "agent_id":
                run.agent_id,
            "question":
                eval_case.question,
            "expected_answer":
                answer,
            "answerable":
                eval_case.answerable,
            "tools_used":
                tools_used,
            "source_metadata":
                source_metadata,
        }
