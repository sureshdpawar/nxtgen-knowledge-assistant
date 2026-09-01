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
    TracerProvider,
)
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

from app.core.config import settings


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
    """

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

    This ID will later connect:

        production interaction
              ↓
        evaluation result
              ↓
        execution trace
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