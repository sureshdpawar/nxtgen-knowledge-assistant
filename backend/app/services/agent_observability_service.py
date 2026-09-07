from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from math import ceil
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AgentRunStatus
from app.models.agent import Agent
from app.models.agent_run import AgentRun
from app.models.llm_usage_event import LLMUsageEvent
from app.models.user import User


class AgentObservabilityService:

    def _get_agent(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
    ) -> Agent:
        stmt = (
            select(Agent)
            .where(
                Agent.id == agent_id,
                Agent.tenant_id == current_user.tenant_id,
            )
        )

        agent = db.scalars(stmt).first()

        if agent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found.",
            )

        return agent

    def _percentile_95(
        self,
        values: list[float],
    ) -> float | None:
        if not values:
            return None

        ordered = sorted(values)
        index = max(
            0,
            ceil(0.95 * len(ordered)) - 1,
        )
        return float(ordered[index])

    def _usage_summary(
        self,
        events: list[LLMUsageEvent],
    ) -> dict:
        input_tokens = sum(
            event.input_tokens for event in events
        )
        output_tokens = sum(
            event.output_tokens for event in events
        )
        total_tokens = sum(
            event.total_tokens for event in events
        )

        total_cost = Decimal("0")
        currencies: set[str] = set()
        pricing_complete = len(events) > 0

        for event in events:
            metadata = event.usage_metadata or {}
            cost = metadata.get("cost")

            if not isinstance(cost, dict):
                pricing_complete = False
                continue

            if not cost.get("pricing_found", False):
                pricing_complete = False
                continue

            event_cost = cost.get("total_cost")
            currency = cost.get("currency")

            if event_cost is None or not currency:
                pricing_complete = False
                continue

            try:
                total_cost += Decimal(str(event_cost))
            except (ValueError, TypeError):
                pricing_complete = False
                continue

            currencies.add(str(currency))

        if len(currencies) != 1:
            pricing_complete = False

        return {
            "request_count": len(events),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost": (
                float(total_cost)
                if pricing_complete
                else None
            ),
            "currency": (
                next(iter(currencies))
                if pricing_complete
                else None
            ),
            "pricing_complete": pricing_complete,
        }

    def get_agent_metrics(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
        hours: int,
    ) -> dict:
        agent = self._get_agent(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )

        window_end = datetime.now(timezone.utc)
        window_start = window_end - timedelta(hours=hours)

        runs = list(
            db.scalars(
                select(AgentRun)
                .where(
                    AgentRun.tenant_id
                    == current_user.tenant_id,
                    AgentRun.agent_id == agent.id,
                    AgentRun.started_at >= window_start,
                    AgentRun.started_at < window_end,
                )
                .order_by(AgentRun.started_at.asc())
            ).all()
        )

        total_runs = len(runs)
        status_counts = Counter(
            run.status for run in runs
        )

        completed_runs = status_counts[
            AgentRunStatus.COMPLETED
        ]
        failed_runs = status_counts[
            AgentRunStatus.FAILED
        ]
        running_runs = status_counts[
            AgentRunStatus.RUNNING
        ]
        waiting_runs = status_counts[
            AgentRunStatus.WAITING_FOR_APPROVAL
        ]

        durations = [
            float(run.duration_ms)
            for run in runs
            if run.duration_ms is not None
            and run.status in {
                AgentRunStatus.COMPLETED,
                AgentRunStatus.FAILED,
            }
        ]

        average_duration_ms = (
            sum(durations) / len(durations)
            if durations
            else None
        )

        total_llm_calls = sum(
            int(run.llm_calls or 0)
            for run in runs
        )

        tool_usage = Counter()
        actor_mix = Counter()
        runs_using_tools = 0

        for run in runs:
            actor_mix[run.actor_type] += 1

            tools = list(run.tools_used or [])
            if tools:
                runs_using_tools += 1

            for tool_name in tools:
                tool_usage[str(tool_name)] += 1

        run_ids = [
            str(run.id) for run in runs
        ]

        usage_events: list[LLMUsageEvent] = []

        if run_ids:
            usage_stmt = (
                select(LLMUsageEvent)
                .where(
                    LLMUsageEvent.tenant_id
                    == current_user.tenant_id,
                    LLMUsageEvent.request_type == "agent",
                    LLMUsageEvent.created_at >= window_start,
                    LLMUsageEvent.created_at < window_end,
                    LLMUsageEvent.usage_metadata[
                        "agent_run_id"
                    ].as_string().in_(run_ids),
                )
            )

            usage_events = list(
                db.scalars(usage_stmt).all()
            )

        return {
            "agent_id": agent.id,
            "window_start": window_start,
            "window_end": window_end,
            "window_hours": hours,
            "total_runs": total_runs,
            "completed_runs": completed_runs,
            "failed_runs": failed_runs,
            "running_runs": running_runs,
            "waiting_for_approval_runs": waiting_runs,
            "completion_rate": (
                completed_runs / total_runs
                if total_runs
                else 0.0
            ),
            "failure_rate": (
                failed_runs / total_runs
                if total_runs
                else 0.0
            ),
            "average_duration_ms": average_duration_ms,
            "p95_duration_ms": self._percentile_95(
                durations
            ),
            "total_llm_calls": total_llm_calls,
            "average_llm_calls_per_run": (
                total_llm_calls / total_runs
                if total_runs
                else 0.0
            ),
            "runs_using_tools": runs_using_tools,
            "tool_usage": [
                {"name": name, "count": count}
                for name, count in tool_usage.most_common()
            ],
            "actor_mix": [
                {"name": name, "count": count}
                for name, count in actor_mix.most_common()
            ],
            "llm_usage": self._usage_summary(
                usage_events
            ),
        }
