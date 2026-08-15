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
from app.exceptions.handlers import (
    register_exception_handlers,
)
from app.middleware.logging import (
    LoggingMiddleware,
)
from app.middleware.request_id import (
    RequestIDMiddleware,
)


setup_logging()


validate_startup_configuration()


app = FastAPI(
    title="NXTGEN Knowledge Assistant API",
    version="1.0.0",
)


cors_origins = [
    origin.strip()
    for origin
    in settings.CORS_ORIGINS.split(",")
    if origin.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=
        cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message":
            "NXTGEN Knowledge Assistant API",
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