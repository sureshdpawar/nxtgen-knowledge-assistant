from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.router import router
from app.api.deps import get_db
from app.exceptions.handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.middleware.logging import LoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware

setup_logging()

app = FastAPI(
    title="NXTGEN Knowledge Assistant API",
    version="1.0.0",
)

@app.get("/")
def root():
    return {
        "message": "NXTGEN Knowledge Assistant API"
    }

@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "database": "connected"
    }

app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)    
register_exception_handlers(app)
app.include_router(router)