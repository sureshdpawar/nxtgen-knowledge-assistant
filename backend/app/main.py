from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.router import router
from app.api.deps import get_db

app = FastAPI(
    title="NXTGEN Knowledge Assistant API",
    version="1.0.0",
)


app.include_router(router)


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