import app.models

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.core.logging import setup_logging
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware


setup_logging()


app = FastAPI(
    title="NXTGEN Knowledge Assistant API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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