from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.auth.permissions import (
    require_admin,
)
from app.core.telemetry import (
    get_finished_spans_for_trace,
    is_memory_trace_debugging_enabled,
    readable_span_to_dict,
    trace_belongs_to_tenant,
)
from app.models.user import User
from app.schemas.trace_debug import (
    TraceDebugRead,
)


router = APIRouter(
    prefix="/trace-debug",
    tags=["Trace Debugging"],
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


@router.get(
    "/traces/{trace_id}",
    response_model=TraceDebugRead,
)
def get_trace_debug(
    trace_id: str,
    current_user: User = Depends(
        require_admin,
    ),
):
    """
    Read one finished OpenTelemetry trace from
    the local in-memory exporter.

    This endpoint is intentionally intended for
    development/debugging. It introduces no
    external observability server.

    In production, the same trace ID should be
    resolved by the configured OTLP backend.
    """

    tenant_id = _require_tenant_id(
        current_user
    )

    if not is_memory_trace_debugging_enabled():
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Local trace debugging is not enabled. "
                "Set OTEL_TRACE_EXPORTER=memory and "
                "restart the backend."
            ),
        )

    spans = get_finished_spans_for_trace(
        trace_id
    )

    if not spans:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Trace not found in this backend "
                "process. Memory traces disappear "
                "after restart."
            ),
        )

    if not trace_belongs_to_tenant(
        spans,
        tenant_id=str(tenant_id),
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Trace not found.",
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
        trace_id=trace_id.lower(),
        span_count=len(
            serialized_spans
        ),
        spans=serialized_spans,
    )
