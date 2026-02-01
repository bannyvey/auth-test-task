from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import HTTPException, Request
import logging

from src.exceptions.custom_exceptions import ServiceError

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки всех ошибок приложения"""

    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            return response

        except ServiceError as exc:
            logger.error(
                f"ServiceError: {exc.message}",
                extra={
                    "code": exc.status_code,
                    "path": request.url.path,
                    "method": request.method
                }
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "detail": exc.public_detail,
                    "code": exc.status_code,
                    "path": str(request.url.path)
                }
            )

        except Exception as exc:
            logger.error(
                str(exc),
                extra={
                    "path": request.url.path,
                    "method": request.method
                }
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "code": "INTERNAL_ERROR",
                    "path": str(request.url.path)
                }
            )


async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
):
    error = exc.errors()[0]
    logger.error(
        msg=error.get("msg"),
    )
    return JSONResponse(
        status_code=422,
        content={
            "detail": error["msg"],
            "code": "VALIDATION_ERROR"
        }
    )


async def http_exception_handler(
        request: Request,
        exc: HTTPException
):
    logger.error(msg=exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "code": exc.status_code,
        }
    )
