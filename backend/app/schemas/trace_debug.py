from typing import Any

from pydantic import BaseModel


class TraceDebugSpanRead(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: str | None

    name: str
    kind: str
    status: str

    start_time_unix_nano: int | None
    end_time_unix_nano: int | None
    duration_ms: float | None

    attributes: dict[str, Any]
    resource: dict[str, Any]


class TraceDebugRead(BaseModel):
    trace_id: str
    span_count: int
    spans: list[TraceDebugSpanRead]
