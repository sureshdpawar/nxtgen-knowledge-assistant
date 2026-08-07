from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.base import AppException


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):

        request.state.error_code = exc.error_code
        request.state.error_message = exc.message

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                }
            },
        )