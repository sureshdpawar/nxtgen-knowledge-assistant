import app.models

from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.api.router import router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.startup_validation import (
    validate_startup_configuration,
)
from app.core.telemetry import (
    configure_telemetry,
)
from app.exceptions.handlers import (
    register_exception_handlers,
)
from app.middleware.logging import (
    LoggingMiddleware,
)
from app.middleware.request_id import (
    RequestIDMiddleware,
)
from app.middleware.widget_cors import (
    WidgetCORSMiddleware,
)


setup_logging()


validate_startup_configuration()


app = FastAPI(
    title=(
        "NXTGEN Knowledge Assistant API"
    ),
    version="1.0.0",
)


#
# ---------------------------------------------------------
# OpenTelemetry
# ---------------------------------------------------------
#
# Instrument the FastAPI application once at startup.
#
# OpenTelemetry remains independent of the eventual
# observability backend. Today spans can be written to the
# console. Later the same instrumentation can export over
# OTLP to a Collector, Datadog, Elastic, Grafana, or another
# compatible backend.
#
configure_telemetry(
    app
)


#
# ---------------------------------------------------------
# Internal application CORS
# ---------------------------------------------------------
#
# This remains intentionally static.
#
# It controls browser access to the authenticated NXTGEN
# application API, such as:
#
# /api/v1/*
#
# Customer Website widget domains should NOT be added here.
#
cors_origins = [
    origin.strip()
    for origin
    in settings.CORS_ORIGINS.split(
        ","
    )
    if origin.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        cors_origins
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#
# ---------------------------------------------------------
# Website Widget CORS
# ---------------------------------------------------------
#
# Handles browser CORS mechanics only for:
#
# /public/v1/widget/*
#
# Actual origin authorization is performed against the
# Website ChatChannel's allowed_origins configuration.
#
app.add_middleware(
    WidgetCORSMiddleware
)


@app.get("/")
def root():
    return {
        "message":
            (
                "NXTGEN Knowledge "
                "Assistant API"
            ),
    }


app.add_middleware(
    RequestIDMiddleware
)


app.add_middleware(
    LoggingMiddleware
)


register_exception_handlers(
    app
)


app.include_router(
    router
)