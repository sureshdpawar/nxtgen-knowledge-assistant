from __future__ import annotations

from datetime import (
    datetime,
    timezone,
)
from uuid import UUID

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.models.agent_online_eval_result import (
    AgentOnlineEvalResult,
)
from app.models.agent_run import AgentRun
from app.models.agent_run_step import AgentRunStep
from app.services.llm_judge_service import (
    LLMJudgeService,
)


class AgentOnlineEvalService:
    """
    Evaluate persisted AgentRuns without replay.

    V1 intentionally separates observed-production evaluation
    from offline regression replay.

    Online evaluation:
    - reads an existing AgentRun and AgentRunSteps
    - never calls AgentExecutionService
    - never calls AgentRuntime
    - never executes tools
    - uses tenant-managed evaluator LLM configuration
    """

    TASK_QUALITY_RUBRIC = """
Evaluate how well the Agent's Actual Answer handles the user's request,
using only the user request and the answer shown here.

A high score means:
- the answer directly addresses the user's request
- the answer is coherent and useful
- limitations or inability are communicated clearly when applicable
- the answer does not claim that an external action succeeded unless the
  answer itself provides a clear basis for that claim
- the answer avoids misleading capability claims

A low score means:
- the answer misunderstands or avoids the request
- the answer is materially irrelevant
- the answer misleadingly claims an unsupported or unverified action
- the answer is contradictory or unusable

Important:
- Do NOT use outside knowledge.
- Do NOT infer factual correctness that cannot be established from the
  request and answer.
- Do NOT assume an unavailable expected/gold answer.
- Judge task handling quality, not hidden business truth.
""".strip()

    def __init__(self):
        self.judge_service = LLMJudgeService()

    def _tenant_id(
        self,
        current_user,
    ) -> UUID:
        tenant_id = getattr(
            current_user,
            "tenant_id",
            None,
        )

        if tenant_id is None:
            raise ValueError(
                "Tenant is required."
            )

        return tenant_id

    def _run_status(
        self,
        run: AgentRun,
    ) -> str:
        return str(
            getattr(
                run.status,
                "value",
                run.status,
            )
        ).upper()

    def _load_run(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        agent_run_id: UUID,
    ) -> AgentRun | None:
        return db.scalar(
            select(
                AgentRun
            ).where(
                AgentRun.id
                == agent_run_id,
                AgentRun.tenant_id
                == tenant_id,
            )
        )

    def _load_steps(
        self,
        db: Session,
        *,
        run_id: UUID,
    ) -> list[AgentRunStep]:
        return list(
            db.scalars(
                select(
                    AgentRunStep
                )
                .where(
                    AgentRunStep.run_id
                    == run_id
                )
                .order_by(
                    AgentRunStep
                    .step_number
                    .asc()
                )
            ).all()
        )

    def _existing(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        agent_run_id: UUID,
    ) -> AgentOnlineEvalResult | None:
        return db.scalar(
            select(
                AgentOnlineEvalResult
            ).where(
                AgentOnlineEvalResult.tenant_id
                == tenant_id,
                AgentOnlineEvalResult.agent_run_id
                == agent_run_id,
            )
        )

    def _step_status(
        self,
        step: AgentRunStep,
    ) -> str:
        return str(
            getattr(
                step.status,
                "value",
                step.status,
            )
        ).upper()

    def _execution_health(
        self,
        *,
        run: AgentRun,
        steps: list[AgentRunStep],
    ) -> tuple[
        float,
        dict,
    ]:
        run_status = self._run_status(
            run
        )

        failed_steps = [
            step
            for step in steps
            if self._step_status(step)
            == "FAILED"
        ]

        if (
            run_status == "FAILED"
            or run.error_message
            or failed_steps
        ):
            score = 0.0
        else:
            score = 1.0

        return (
            score,
            {
                "score": score,
                "run_status": run_status,
                "run_error": (
                    run.error_message
                    or None
                ),
                "step_count": len(steps),
                "failed_step_count": (
                    len(failed_steps)
                ),
                "failed_steps": [
                    {
                        "step_number":
                            step.step_number,
                        "step_type": str(
                            getattr(
                                step.step_type,
                                "value",
                                step.step_type,
                            )
                        ),
                        "name": step.name,
                    }
                    for step in failed_steps
                ],
                "deterministic": True,
            },
        )

    def evaluate_run(
        self,
        db: Session,
        *,
        current_user,
        agent_run_id: UUID,
        evaluator_llm_configuration_id:
            UUID | None = None,
        task_quality_threshold:
            float = 0.80,
    ) -> AgentOnlineEvalResult:
        if (
            task_quality_threshold < 0.0
            or task_quality_threshold > 1.0
        ):
            raise ValueError(
                "Task quality threshold must "
                "be between 0 and 1."
            )

        tenant_id = self._tenant_id(
            current_user
        )

        run = self._load_run(
            db,
            tenant_id=tenant_id,
            agent_run_id=agent_run_id,
        )

        if run is None:
            raise ValueError(
                "Agent run not found."
            )

        run_status = self._run_status(
            run
        )

        if run_status not in {
            "COMPLETED",
            "FAILED",
        }:
            raise ValueError(
                "Only completed or failed AgentRuns "
                "can be evaluated online."
            )

        result = self._existing(
            db,
            tenant_id=tenant_id,
            agent_run_id=agent_run_id,
        )

        if result is None:
            result = AgentOnlineEvalResult(
                tenant_id=tenant_id,
                agent_id=run.agent_id,
                agent_run_id=run.id,
                status="pending",
                sample_reason="manual",
                question=run.query,
                actual_answer=run.answer,
                tools_used=list(
                    run.tools_used
                    or []
                ),
                metrics={},
                evaluation_metadata={},
            )
            db.add(
                result
            )
            db.flush()
        else:
            result.question = run.query
            result.actual_answer = run.answer
            result.tools_used = list(
                run.tools_used
                or []
            )
            result.error_message = None

        result.status = "running"
        db.flush()

        steps = self._load_steps(
            db,
            run_id=run.id,
        )

        (
            execution_health_score,
            execution_health_metadata,
        ) = self._execution_health(
            run=run,
            steps=steps,
        )

        result.execution_health_score = (
            execution_health_score
        )

        metrics = {
            "execution_health":
                execution_health_metadata,
        }

        try:
            if run.answer:
                task_quality = (
                    self.judge_service.judge(
                        db=db,
                        tenant_id=tenant_id,
                        evaluator_llm_configuration_id=(
                            evaluator_llm_configuration_id
                        ),
                        metric_name=(
                            "agent_task_quality"
                        ),
                        rubric=(
                            self.TASK_QUALITY_RUBRIC
                        ),
                        question=run.query,
                        actual_answer=run.answer,
                        retrieved_context=[],
                        expected_answer=None,
                        answerable=None,
                        threshold=(
                            task_quality_threshold
                        ),
                    )
                )

                result.task_quality_score = (
                    task_quality.score
                )

                metrics["task_quality"] = {
                    "score":
                        task_quality.score,
                    "passed":
                        task_quality.passed,
                    "reason":
                        task_quality.reason,
                    "usage":
                        task_quality.usage,
                    "latency_ms":
                        task_quality.latency_ms,
                    "evaluator":
                        task_quality
                        .evaluator_metadata,
                    "threshold":
                        task_quality_threshold,
                }

                scores = [
                    task_quality.score,
                    execution_health_score,
                ]

                result.overall_score = (
                    sum(scores)
                    / len(scores)
                )

                result.passed = bool(
                    task_quality.passed
                    and execution_health_score
                    >= 1.0
                )

            else:
                result.task_quality_score = None
                result.overall_score = (
                    execution_health_score
                )
                result.passed = False

                metrics["task_quality"] = {
                    "score": None,
                    "passed": False,
                    "reason": (
                        "AgentRun has no persisted "
                        "answer to evaluate."
                    ),
                    "threshold":
                        task_quality_threshold,
                }

            result.metrics = metrics
            result.evaluated_at = (
                datetime.now(
                    timezone.utc
                )
            )
            result.status = "completed"

            metadata = dict(
                result.evaluation_metadata
                or {}
            )

            metadata.update(
                {
                    "evaluation_kind":
                        "agent_online",
                    "evaluation_mode":
                        "existing_run_no_replay",
                    "agent_run_status":
                        run_status,
                    "actor_type":
                        run.actor_type,
                    "actor_id":
                        run.actor_id,
                    "thread_id": (
                        str(run.thread_id)
                        if run.thread_id
                        else None
                    ),
                    "llm_calls":
                        run.llm_calls,
                    "duration_ms":
                        run.duration_ms,
                    "evaluator_llm_configuration_id": (
                        str(
                            evaluator_llm_configuration_id
                        )
                        if evaluator_llm_configuration_id
                        else None
                    ),
                    "task_quality_threshold":
                        task_quality_threshold,
                    "side_effect_free":
                        True,
                    "replayed":
                        False,
                }
            )

            result.evaluation_metadata = (
                metadata
            )

            db.commit()
            db.refresh(
                result
            )

            return result

        except Exception as exc:
            result.status = "failed"
            result.error_message = str(
                exc
            )
            result.evaluated_at = (
                datetime.now(
                    timezone.utc
                )
            )
            result.metrics = metrics

            db.commit()
            db.refresh(
                result
            )

            raise

    def process_pending(
        self,
        db: Session,
        *,
        current_user,
        limit: int = 20,
        evaluator_llm_configuration_id:
            UUID | None = None,
        task_quality_threshold:
            float = 0.80,
    ) -> dict:
        """
        Evaluate a bounded batch of pending
        production Agent-quality samples.

        The captured AgentRuns are never replayed.
        """

        tenant_id = self._tenant_id(
            current_user
        )

        bounded_limit = max(
            1,
            min(
                int(limit),
                100,
            ),
        )

        result_ids = list(
            db.scalars(
                select(
                    AgentOnlineEvalResult.id
                )
                .where(
                    AgentOnlineEvalResult.tenant_id
                    == tenant_id,
                    AgentOnlineEvalResult.status
                    == "pending",
                )
                .order_by(
                    AgentOnlineEvalResult
                    .created_at
                    .asc()
                )
                .limit(
                    bounded_limit
                )
            ).all()
        )

        completed = 0
        failed = 0
        processed_ids: list[UUID] = []

        for result_id in result_ids:
            candidate = db.get(
                AgentOnlineEvalResult,
                result_id,
            )

            if (
                candidate is None
                or candidate.tenant_id
                != tenant_id
            ):
                continue

            try:
                evaluated = self.evaluate_run(
                    db,
                    current_user=current_user,
                    agent_run_id=(
                        candidate.agent_run_id
                    ),
                    evaluator_llm_configuration_id=(
                        evaluator_llm_configuration_id
                    ),
                    task_quality_threshold=(
                        task_quality_threshold
                    ),
                )

                processed_ids.append(
                    evaluated.id
                )

                if (
                    evaluated.status
                    == "completed"
                ):
                    completed += 1
                else:
                    failed += 1

            except Exception:
                processed_ids.append(
                    result_id
                )
                failed += 1

        return {
            "requested":
                len(result_ids),
            "processed":
                len(processed_ids),
            "completed":
                completed,
            "failed":
                failed,
            "result_ids":
                processed_ids,
        }

    def list_results(
        self,
        db: Session,
        *,
        current_user,
        agent_id: UUID | None = None,
        passed: bool | None = None,
        limit: int = 100,
    ) -> list[
        AgentOnlineEvalResult
    ]:
        tenant_id = self._tenant_id(
            current_user
        )

        query = (
            select(
                AgentOnlineEvalResult
            )
            .where(
                AgentOnlineEvalResult.tenant_id
                == tenant_id
            )
        )

        if agent_id is not None:
            query = query.where(
                AgentOnlineEvalResult.agent_id
                == agent_id
            )

        if passed is not None:
            query = query.where(
                AgentOnlineEvalResult.passed
                == passed
            )

        query = (
            query
            .order_by(
                AgentOnlineEvalResult
                .created_at
                .desc()
            )
            .limit(
                max(
                    1,
                    min(
                        limit,
                        500,
                    ),
                )
            )
        )

        return list(
            db.scalars(
                query
            ).all()
        )

    def get_result(
        self,
        db: Session,
        *,
        current_user,
        result_id: UUID,
    ) -> AgentOnlineEvalResult | None:
        tenant_id = self._tenant_id(
            current_user
        )

        return db.scalar(
            select(
                AgentOnlineEvalResult
            ).where(
                AgentOnlineEvalResult.id
                == result_id,
                AgentOnlineEvalResult.tenant_id
                == tenant_id,
            )
        )

    def summary(
        self,
        db: Session,
        *,
        current_user,
        agent_id: UUID | None = None,
    ) -> dict:
        tenant_id = self._tenant_id(
            current_user
        )

        filters = [
            AgentOnlineEvalResult.tenant_id
            == tenant_id
        ]

        if agent_id is not None:
            filters.append(
                AgentOnlineEvalResult.agent_id
                == agent_id
            )

        total = int(
            db.scalar(
                select(
                    func.count(
                        AgentOnlineEvalResult.id
                    )
                ).where(
                    *filters
                )
            )
            or 0
        )

        pending = int(
            db.scalar(
                select(
                    func.count(
                        AgentOnlineEvalResult.id
                    )
                ).where(
                    *filters,
                    AgentOnlineEvalResult.status
                    == "pending",
                )
            )
            or 0
        )

        completed = int(
            db.scalar(
                select(
                    func.count(
                        AgentOnlineEvalResult.id
                    )
                ).where(
                    *filters,
                    AgentOnlineEvalResult.status
                    == "completed",
                )
            )
            or 0
        )

        failed = int(
            db.scalar(
                select(
                    func.count(
                        AgentOnlineEvalResult.id
                    )
                ).where(
                    *filters,
                    AgentOnlineEvalResult.status
                    == "failed",
                )
            )
            or 0
        )

        passed_count = int(
            db.scalar(
                select(
                    func.count(
                        AgentOnlineEvalResult.id
                    )
                ).where(
                    *filters,
                    AgentOnlineEvalResult.status
                    == "completed",
                    AgentOnlineEvalResult.passed
                    .is_(True),
                )
            )
            or 0
        )

        failed_quality = int(
            db.scalar(
                select(
                    func.count(
                        AgentOnlineEvalResult.id
                    )
                ).where(
                    *filters,
                    AgentOnlineEvalResult.status
                    == "completed",
                    AgentOnlineEvalResult.passed
                    .is_(False),
                )
            )
            or 0
        )

        averages = db.execute(
            select(
                func.avg(
                    AgentOnlineEvalResult
                    .task_quality_score
                ),
                func.avg(
                    AgentOnlineEvalResult
                    .execution_health_score
                ),
                func.avg(
                    AgentOnlineEvalResult
                    .overall_score
                ),
            ).where(
                *filters,
                AgentOnlineEvalResult.status
                == "completed",
            )
        ).one()

        pass_rate = (
            passed_count
            / completed
            if completed
            else None
        )

        return {
            "total": total,
            "pending": pending,
            "completed": completed,
            "failed": failed,
            "passed": passed_count,
            "failed_quality":
                failed_quality,
            "pass_rate":
                pass_rate,
            "average_task_quality": (
                float(averages[0])
                if averages[0]
                is not None
                else None
            ),
            "average_execution_health": (
                float(averages[1])
                if averages[1]
                is not None
                else None
            ),
            "average_overall_score": (
                float(averages[2])
                if averages[2]
                is not None
                else None
            ),
        }
