import hashlib

from datetime import datetime
from uuid import (
    UUID,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import (
    select,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_admin,
)
from app.core.telemetry import (
    get_finished_spans_for_trace,
    is_memory_trace_debugging_enabled,
    readable_span_to_dict,
    trace_belongs_to_tenant,
)
from app.db.session import get_db
from app.models.agent_run import (
    AgentRun,
)
from app.models.agent_run_step import (
    AgentRunStep,
)
from app.models.user import User
from app.repositories.online_eval_result_repository import (
    OnlineEvalResultRepository,
)
from app.schemas.trace_debug import (
    TraceDebugRead,
)


router = APIRouter(
    prefix="/trace-debug",
    tags=["Trace Debugging"],
)


online_eval_repository = (
    OnlineEvalResultRepository()
)


def _require_tenant_id(
    current_user: User,
) -> UUID:
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail="Tenant is required.",
        )

    return current_user.tenant_id


def _normalize_trace_id(
    trace_id: str,
) -> str:
    normalized = (
        trace_id
        .strip()
        .lower()
    )

    if (
        len(normalized) != 32
        or any(
            char not in
            "0123456789abcdef"
            for char in normalized
        )
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Trace not found.",
        )

    return normalized


def _datetime_to_unix_nano(
    value: datetime | None,
) -> int | None:
    if value is None:
        return None

    return int(
        value.timestamp()
        * 1_000_000_000
    )


def _stable_span_id(
    *parts: str,
) -> str:
    """
    Build a deterministic 16-character
    hexadecimal span identifier for a durable
    application trace reconstructed from DB
    records.
    """

    payload = ":".join(
        str(part)
        for part in parts
    )

    return (
        hashlib.sha256(
            payload.encode(
                "utf-8"
            )
        )
        .hexdigest()[:16]
    )


def _read_persisted_online_eval_trace(
    db: Session,
    *,
    tenant_id: UUID,
    trace_id: str,
) -> TraceDebugRead | None:
    """
    Resolve a durable OpenTelemetry span snapshot
    captured with an online-evaluation sample.
    """

    results = (
        online_eval_repository
        .list_by_trace_id(
            db=db,
            tenant_id=tenant_id,
            source_trace_id=trace_id,
        )
    )

    for result in results:
        metadata = (
            result.evaluation_metadata
            or {}
        )

        snapshot = metadata.get(
            "source_trace_snapshot"
        )

        if not isinstance(
            snapshot,
            dict,
        ):
            continue

        snapshot_trace_id = (
            str(
                snapshot.get(
                    "trace_id"
                )
                or ""
            )
            .strip()
            .lower()
        )

        if (
            snapshot_trace_id
            != trace_id
        ):
            continue

        spans = snapshot.get(
            "spans"
        )

        if not isinstance(
            spans,
            list,
        ):
            continue

        return TraceDebugRead(
            trace_id=trace_id,
            span_count=len(
                spans
            ),
            spans=spans,
        )

    return None


def _read_agent_run_trace(
    db: Session,
    *,
    tenant_id: UUID,
    trace_id: str,
) -> TraceDebugRead | None:
    """
    Reconstruct a durable production execution
    path for Agent Chat from AgentRun and
    AgentRunStep rows.

    Agent online-evaluation capture persists
    agent_run_id in evaluation_metadata. Those
    run and step rows survive backend restarts,
    so this path remains available even when the
    local OpenTelemetry memory exporter has been
    cleared.

    This is an application-level durable trace,
    not a replacement for a full OTLP backend.
    """

    results = (
        online_eval_repository
        .list_by_trace_id(
            db=db,
            tenant_id=tenant_id,
            source_trace_id=trace_id,
        )
    )

    for result in results:
        metadata = (
            result.evaluation_metadata
            or {}
        )

        if (
            metadata.get(
                "capture_source"
            )
            != "agent"
            and metadata.get(
                "workload"
            )
            != "agent"
        ):
            continue

        raw_run_id = metadata.get(
            "agent_run_id"
        )

        if not raw_run_id:
            continue

        try:
            run_id = UUID(
                str(
                    raw_run_id
                )
            )
        except (
            ValueError,
            TypeError,
        ):
            continue

        run = db.scalar(
            select(
                AgentRun
            )
            .where(
                AgentRun.id
                == run_id,
                AgentRun.tenant_id
                == tenant_id,
            )
        )

        if run is None:
            continue

        steps = (
            db.execute(
                select(
                    AgentRunStep
                )
                .where(
                    AgentRunStep.run_id
                    == run.id
                )
                .order_by(
                    AgentRunStep
                    .step_number
                    .asc()
                )
            )
            .scalars()
            .all()
        )

        root_span_id = (
            _stable_span_id(
                trace_id,
                str(
                    run.id
                ),
                "root",
            )
        )

        start_nano = (
            _datetime_to_unix_nano(
                run.started_at
            )
        )

        end_nano = (
            _datetime_to_unix_nano(
                run.completed_at
            )
        )

        root_status = (
            "ERROR"
            if str(
                getattr(
                    run.status,
                    "value",
                    run.status,
                )
            ).upper()
            == "FAILED"
            else "OK"
        )

        spans: list[dict] = [
            {
                "trace_id":
                    trace_id,
                "span_id":
                    root_span_id,
                "parent_span_id":
                    None,
                "name":
                    "agent.run",
                "kind":
                    "INTERNAL",
                "status":
                    root_status,
                "start_time_unix_nano":
                    start_nano,
                "end_time_unix_nano":
                    end_nano,
                "duration_ms":
                    run.duration_ms,
                "attributes": {
                    "knowgentiq.tenant.id":
                        str(
                            run.tenant_id
                        ),
                    "knowgentiq.agent.id":
                        str(
                            run.agent_id
                        ),
                    "knowgentiq.agent.run.id":
                        str(
                            run.id
                        ),
                    "knowgentiq.agent.thread.id":
                        (
                            str(
                                run.thread_id
                            )
                            if run.thread_id
                            else ""
                        ),
                    "knowgentiq.agent.actor.type":
                        run.actor_type,
                    "knowgentiq.agent.actor.id":
                        run.actor_id,
                    "knowgentiq.agent.llm_calls":
                        run.llm_calls,
                    "knowgentiq.trace.storage":
                        "agent_run_database",
                },
                "resource": {
                    "service.name":
                        "nxtgen-backend",
                },
            }
        ]

        cursor_nano = start_nano

        for step in steps:
            duration_ms = (
                float(
                    step.duration_ms
                )
                if step.duration_ms
                is not None
                else None
            )

            step_start_nano = (
                cursor_nano
            )

            step_end_nano = None

            if (
                step_start_nano
                is not None
                and duration_ms
                is not None
            ):
                step_end_nano = (
                    step_start_nano
                    + int(
                        duration_ms
                        * 1_000_000
                    )
                )

                cursor_nano = (
                    step_end_nano
                )

            status_value = str(
                getattr(
                    step.status,
                    "value",
                    step.status,
                )
            ).upper()

            step_status = (
                "ERROR"
                if status_value
                == "FAILED"
                else "OK"
            )

            step_type = str(
                getattr(
                    step.step_type,
                    "value",
                    step.step_type,
                )
            )

            spans.append(
                {
                    "trace_id":
                        trace_id,
                    "span_id":
                        _stable_span_id(
                            trace_id,
                            str(
                                run.id
                            ),
                            str(
                                step.id
                            ),
                            str(
                                step.step_number
                            ),
                        ),
                    "parent_span_id":
                        root_span_id,
                    "name":
                        step.name,
                    "kind":
                        "INTERNAL",
                    "status":
                        step_status,
                    "start_time_unix_nano":
                        step_start_nano,
                    "end_time_unix_nano":
                        step_end_nano,
                    "duration_ms":
                        duration_ms,
                    "attributes": {
                        "knowgentiq.tenant.id":
                            str(
                                run.tenant_id
                            ),
                        "knowgentiq.agent.id":
                            str(
                                run.agent_id
                            ),
                        "knowgentiq.agent.run.id":
                            str(
                                run.id
                            ),
                        "knowgentiq.agent.step.id":
                            str(
                                step.id
                            ),
                        "knowgentiq.agent.step.number":
                            step.step_number,
                        "knowgentiq.agent.step.type":
                            step_type,
                        "knowgentiq.agent.step.status":
                            status_value,
                        "knowgentiq.trace.storage":
                            "agent_run_database",
                    },
                    "resource": {
                        "service.name":
                            "nxtgen-backend",
                    },
                }
            )

        return TraceDebugRead(
            trace_id=trace_id,
            span_count=len(
                spans
            ),
            spans=spans,
        )

    return None


@router.get(
    "/traces/{trace_id}",
    response_model=TraceDebugRead,
)
def get_trace_debug(
    trace_id: str,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    """
    Read one production execution trace.

    Resolution order:

    1. Current-process in-memory OpenTelemetry
       spans, when memory tracing is enabled.

    2. Durable OpenTelemetry span snapshot
       persisted with an online-evaluation sample.

    3. For Agent Chat samples, reconstruct the
       durable execution path from persisted
       AgentRun and AgentRunStep records.

    The AgentRun fallback makes old and new Agent
    online-evaluation Source Trace links useful
    across backend restarts without requiring an
    external observability server.

    A proper OTLP backend remains the production
    trace store for full infrastructure-level
    traces.
    """

    tenant_id = _require_tenant_id(
        current_user
    )

    normalized_trace_id = (
        _normalize_trace_id(
            trace_id
        )
    )

    if (
        is_memory_trace_debugging_enabled()
    ):
        spans = (
            get_finished_spans_for_trace(
                normalized_trace_id
            )
        )

        if spans:
            if not trace_belongs_to_tenant(
                spans,
                tenant_id=
                    str(
                        tenant_id
                    ),
            ):
                raise HTTPException(
                    status_code=(
                        status.HTTP_404_NOT_FOUND
                    ),
                    detail=(
                        "Trace not found."
                    ),
                )

            serialized_spans = [
                readable_span_to_dict(
                    span
                )
                for span in spans
            ]

            serialized_spans.sort(
                key=lambda item: (
                    item.get(
                        "start_time_unix_nano"
                    )
                    or 0
                )
            )

            return TraceDebugRead(
                trace_id=
                    normalized_trace_id,
                span_count=len(
                    serialized_spans
                ),
                spans=
                    serialized_spans,
            )

    persisted = (
        _read_persisted_online_eval_trace(
            db,
            tenant_id=
                tenant_id,
            trace_id=
                normalized_trace_id,
        )
    )

    if persisted is not None:
        return persisted

    agent_trace = (
        _read_agent_run_trace(
            db,
            tenant_id=
                tenant_id,
            trace_id=
                normalized_trace_id,
        )
    )

    if agent_trace is not None:
        return agent_trace

    raise HTTPException(
        status_code=(
            status.HTTP_404_NOT_FOUND
        ),
        detail=(
            "Trace details are not available. "
            "No live OpenTelemetry spans, "
            "persisted trace snapshot, or "
            "durable AgentRun execution path "
            "could be resolved for this trace."
        ),
    )
