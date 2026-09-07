from typing import Any

from fastapi import FastAPI
from loguru import logger
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import (
    FastAPIInstrumentor,
)
from opentelemetry.sdk.resources import (
    Resource,
)
from opentelemetry.sdk.trace import (
    ReadableSpan,
    TracerProvider,
)
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from app.core.config import settings


_memory_exporter: InMemorySpanExporter | None = None


def configure_telemetry(
    app: FastAPI,
) -> None:
    """
    Configure OpenTelemetry tracing for the
    Knowgentiq backend.

    OpenTelemetry is the application's
    observability abstraction.

    The backend receiving telemetry is
    intentionally configurable so Knowgentiq
    remains independent of Grafana, Datadog,
    Elastic, or another provider.

    The "memory" exporter is intentionally a
    local-development debugging backend. It
    keeps finished spans inside this backend
    process so the UI can inspect a trace
    without introducing another server.

    Memory traces disappear on process restart
    and are not intended for production.
    """

    global _memory_exporter

    if not settings.OTEL_ENABLED:
        logger.info(
            "OpenTelemetry tracing disabled"
        )
        return

    resource = Resource.create(
        {
            "service.name": (
                settings.OTEL_SERVICE_NAME
            ),
            "deployment.environment.name": (
                settings.ENVIRONMENT
            ),
        }
    )

    tracer_provider = TracerProvider(
        resource=resource
    )

    exporter_name = (
        settings.OTEL_TRACE_EXPORTER
    )

    if exporter_name == "console":
        tracer_provider.add_span_processor(
            BatchSpanProcessor(
                ConsoleSpanExporter()
            )
        )

    elif exporter_name == "memory":
        _memory_exporter = (
            InMemorySpanExporter()
        )

        tracer_provider.add_span_processor(
            SimpleSpanProcessor(
                _memory_exporter
            )
        )

    elif exporter_name == "otlp":
        endpoint = (
            settings
            .OTEL_EXPORTER_OTLP_TRACES_ENDPOINT
        )

        if not endpoint:
            raise ValueError(
                "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT "
                "must be configured when "
                "OTEL_TRACE_EXPORTER=otlp."
            )

        tracer_provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=endpoint,
                )
            )
        )

    trace.set_tracer_provider(
        tracer_provider
    )

    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=tracer_provider,
    )

    logger.info(
        "OpenTelemetry tracing configured "
        "service={} exporter={}",
        settings.OTEL_SERVICE_NAME,
        exporter_name,
    )


def get_tracer(
    name: str,
):
    """
    Return an OpenTelemetry tracer.

    Application services should use this
    helper rather than constructing their
    own TracerProvider.
    """

    return trace.get_tracer(
        name
    )


def get_current_trace_id() -> (
    str | None
):
    """
    Return the current OpenTelemetry trace ID
    as a 32-character hexadecimal string.
    """

    span = trace.get_current_span()

    span_context = (
        span.get_span_context()
    )

    if not span_context.is_valid:
        return None

    return format(
        span_context.trace_id,
        "032x",
    )


def get_current_span_id() -> (
    str | None
):
    """
    Return the current span ID as a
    16-character hexadecimal string.
    """

    span = trace.get_current_span()

    span_context = (
        span.get_span_context()
    )

    if not span_context.is_valid:
        return None

    return format(
        span_context.span_id,
        "016x",
    )


def is_memory_trace_debugging_enabled() -> bool:
    return (
        settings.OTEL_ENABLED
        and settings.OTEL_TRACE_EXPORTER
        == "memory"
        and _memory_exporter is not None
    )


def get_finished_spans_for_trace(
    trace_id: str,
) -> list[ReadableSpan]:
    """
    Return finished spans for one trace from
    the local in-memory exporter.

    This helper deliberately returns no spans
    when another exporter is configured.
    """

    if not is_memory_trace_debugging_enabled():
        return []

    normalized_trace_id = (
        trace_id.strip().lower()
    )

    if (
        len(normalized_trace_id) != 32
        or any(
            char not in "0123456789abcdef"
            for char in normalized_trace_id
        )
    ):
        return []

    assert _memory_exporter is not None

    spans = (
        _memory_exporter
        .get_finished_spans()
    )

    return [
        span
        for span in spans
        if format(
            span.context.trace_id,
            "032x",
        ) == normalized_trace_id
    ]


def trace_belongs_to_tenant(
    spans: list[ReadableSpan],
    *,
    tenant_id: str,
) -> bool:
    """
    A trace is considered tenant-owned when
    at least one application span explicitly
    carries the tenant attribute.

    Once ownership is established, the API
    may return the full trace including parent
    FastAPI spans that do not independently
    carry tenant metadata.
    """

    expected_tenant_id = str(
        tenant_id
    )

    for span in spans:
        attributes = (
            span.attributes
            or {}
        )

        if (
            attributes.get(
                "knowgentiq.tenant.id"
            )
            == expected_tenant_id
        ):
            return True

    return False


def readable_span_to_dict(
    span: ReadableSpan,
) -> dict[str, Any]:
    """
    Convert a finished OTel span into a
    JSON-safe debugging representation.

    Span attributes should remain metadata-
    only. Question, answer, prompt, and chunk
    text belong in application data stores,
    not OpenTelemetry.
    """

    context = span.context

    parent_span_id = None

    if (
        span.parent is not None
        and span.parent.is_valid
    ):
        parent_span_id = format(
            span.parent.span_id,
            "016x",
        )

    duration_ms = None

    if (
        span.start_time is not None
        and span.end_time is not None
    ):
        duration_ms = (
            span.end_time
            - span.start_time
        ) / 1_000_000

    status_code = (
        span.status.status_code.name
        if span.status is not None
        else "UNSET"
    )

    resource_attributes = dict(
        span.resource.attributes
        if span.resource is not None
        else {}
    )

    return {
        "trace_id": format(
            context.trace_id,
            "032x",
        ),
        "span_id": format(
            context.span_id,
            "016x",
        ),
        "parent_span_id": parent_span_id,
        "name": span.name,
        "kind": span.kind.name,
        "status": status_code,
        "start_time_unix_nano": (
            span.start_time
        ),
        "end_time_unix_nano": (
            span.end_time
        ),
        "duration_ms": duration_ms,
        "attributes": dict(
            span.attributes
            or {}
        ),
        "resource": resource_attributes,
    }
