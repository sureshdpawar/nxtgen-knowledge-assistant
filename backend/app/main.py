from fastapi import FastAPI

app = FastAPI(
    title="NXTGEN Knowledge Assistant API",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "NXTGEN Knowledge Assistant API is running."
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }