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

from app.models.agent import Agent
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
Evaluate how well the Agent's Actual Answer handled the user's request
given the authoritative runtime capability context supplied below.

The runtime capability list represents the actions this Agent was configured
to execute for the sampled run. Treat it as the capability boundary.

A high score means:
- the answer directly addresses the user's request
- the answer is coherent and useful
- if the request requires an external action, that action is supported by an
  available runtime capability
- when the requested action is unavailable, the answer clearly communicates
  that limitation
- supported alternatives may be offered, but they must be clearly presented
  as alternatives rather than fulfillment of the original request
- the answer does not claim an action succeeded unless the persisted executed
  tools support that claim

A low score means:
- the answer claims, promises, initiates, or implies an external action that
  is not supported by the available runtime capabilities
- the answer substitutes a different available action and presents it as if
  it fulfills the user's requested action
- the answer asks for fields needed for a proxy action before the user has
  chosen that alternative
- the answer claims an action succeeded although the corresponding tool did
  not execute
- the answer materially misunderstands or avoids the request

Important:
- Do NOT use outside knowledge.
- Do NOT invent capabilities.
- Tool risk does NOT determine execution permission.
- Explicit execution policy is separate from risk.
- If no gold answer exists, judge correct capability-grounded task handling,
  not hidden business truth.
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

    def _configured_capabilities(
        self,
        *,
        agent: Agent,
    ) -> list[dict]:
        capabilities: list[dict] = []

        if agent.knowledge_base_links:
            capabilities.append(
                {
                    "name":
                        "search_knowledge",
                    "description": (
                        "Search the knowledge bases "
                        "assigned to this Agent."
                    ),
                    "kind":
                        "knowledge",
                    "risk_level":
                        "READ",
                    "execution_policy":
                        "AUTO",
                }
            )

        for link in agent.tool_links:
            tool = getattr(
                link,
                "tool",
                None,
            )

            if tool is None:
                continue

            if not bool(
                getattr(
                    tool,
                    "is_active",
                    False,
                )
            ):
                continue

            integration = getattr(
                tool,
                "integration",
                None,
            )

            if (
                integration is not None
                and not bool(
                    getattr(
                        integration,
                        "is_active",
                        False,
                    )
                )
            ):
                continue

            name = str(
                getattr(
                    tool,
                    "name",
                    "",
                )
                or ""
            ).strip()

            if not name:
                continue

            capabilities.append(
                {
                    "name":
                        name,
                    "description":
                        str(
                            getattr(
                                tool,
                                "description",
                                "",
                            )
                            or ""
                        ).strip(),
                    "kind":
                        str(
                            getattr(
                                getattr(
                                    tool,
                                    "tool_type",
                                    None,
                                ),
                                "value",
                                getattr(
                                    tool,
                                    "tool_type",
                                    "",
                                ),
                            )
                            or ""
                        ),
                    "risk_level":
                        str(
                            getattr(
                                getattr(
                                    tool,
                                    "risk_level",
                                    None,
                                ),
                                "value",
                                getattr(
                                    tool,
                                    "risk_level",
                                    "",
                                ),
                            )
                            or ""
                        ),
                    "execution_policy":
                        str(
                            getattr(
                                getattr(
                                    link,
                                    "execution_policy",
                                    None,
                                ),
                                "value",
                                getattr(
                                    link,
                                    "execution_policy",
                                    "",
                                ),
                            )
                            or ""
                        ),
                }
            )

        return capabilities

    def _capability_context(
        self,
        db: Session,
        *,
        run: AgentRun,
        result: AgentOnlineEvalResult,
    ) -> tuple[
        list[dict],
        str,
    ]:
        metadata = (
            result.evaluation_metadata
            or {}
        )

        captured = metadata.get(
            "runtime_capabilities"
        )

        if isinstance(
            captured,
            list,
        ):
            return (
                [
                    item
                    for item in captured
                    if isinstance(
                        item,
                        dict,
                    )
                ],
                str(
                    metadata.get(
                        "capability_snapshot_source",
                        "capture_time",
                    )
                ),
            )

        agent = db.get(
            Agent,
            run.agent_id,
        )

        if agent is None:
            return (
                [],
                "unavailable",
            )

        return (
            self._configured_capabilities(
                agent=agent,
            ),
            "current_agent_configuration_fallback",
        )

    def _format_capability_context(
        self,
        *,
        capabilities: list[dict],
        tools_used: list[str],
    ) -> str:
        lines = [
            "AUTHORITATIVE AGENT CAPABILITY CONTEXT",
            "",
            "AVAILABLE RUNTIME CAPABILITIES:",
        ]

        if capabilities:
            for item in capabilities:
                name = str(
                    item.get(
                        "name",
                        "",
                    )
                ).strip()

                if not name:
                    continue

                description = str(
                    item.get(
                        "description",
                        "",
                    )
                    or ""
                ).strip()

                execution_policy = str(
                    item.get(
                        "execution_policy",
                        "",
                    )
                    or ""
                ).strip()

                risk_level = str(
                    item.get(
                        "risk_level",
                        "",
                    )
                    or ""
                ).strip()

                details: list[str] = []

                if description:
                    details.append(
                        description
                    )

                if execution_policy:
                    details.append(
                        "execution_policy="
                        + execution_policy
                    )

                if risk_level:
                    details.append(
                        "risk_level="
                        + risk_level
                    )

                suffix = (
                    " — "
                    + "; ".join(
                        details
                    )
                    if details
                    else ""
                )

                lines.append(
                    f"- {name}{suffix}"
                )
        else:
            lines.append(
                "- None recorded"
            )

        lines.extend(
            [
                "",
                "TOOLS ACTUALLY EXECUTED:",
            ]
        )

        if tools_used:
            lines.extend(
                f"- {name}"
                for name in tools_used
            )
        else:
            lines.append(
                "- None"
            )

        lines.extend(
            [
                "",
                (
                    "Use this capability context only to "
                    "judge whether the response truthfully "
                    "handled what the Agent could execute."
                ),
            ]
        )

        return "\n".join(
            lines
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

        (
            runtime_capabilities,
            capability_snapshot_source,
        ) = self._capability_context(
            db,
            run=run,
            result=result,
        )

        capability_context = (
            self._format_capability_context(
                capabilities=
                    runtime_capabilities,
                tools_used=list(
                    run.tools_used
                    or []
                ),
            )
        )

        metrics = {
            "execution_health":
                execution_health_metadata,
            "capability_grounding": {
                "runtime_capabilities":
                    runtime_capabilities,
                "tools_executed":
                    list(
                        run.tools_used
                        or []
                    ),
                "snapshot_source":
                    capability_snapshot_source,
            },
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
                        retrieved_context=[
                            capability_context
                        ],
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
                    "runtime_capabilities":
                        runtime_capabilities,
                    "capability_snapshot_source":
                        capability_snapshot_source,
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
