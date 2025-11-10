"""
Centralized exception handlers for FastAPI

This module registers global exception handlers that convert
application exceptions to proper HTTP responses.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import BaseAppException
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI):
    """Register all exception handlers"""

    @app.exception_handler(BaseAppException)
    async def app_exception_handler(request: Request, exc: BaseAppException):
        """
        Handle all application exceptions

        Returns structured error response with:
        - error code
        - error message
        - additional details
        """
        logger.error(
            "application_error",
            error_code=exc.error_code,
            error_message=exc.message,
            path=request.url.path,
            method=request.method,
            status_code=exc.status_code,
            details=exc.details,
            exc_info=True
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle Pydantic validation errors

        Returns detailed validation error information
        """
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })

        logger.warning(
            "validation_error",
            path=request.url.path,
            method=request.method,
            errors=errors
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "ERR_VALIDATION_001",
                    "message": "Validation error",
                    "details": {
                        "validation_errors": errors
                    }
                }
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        """
        Handle database errors

        Don't expose internal database errors to users
        """
        logger.error(
            "database_error",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            exc_info=True
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "ERR_DB_001",
                    "message": "Database error occurred",
                    "details": {}
                }
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """
        Handle all unhandled exceptions

        This is the catch-all handler
        """
        logger.error(
            "unhandled_exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            error_type=type(exc).__name__,
            exc_info=True
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "ERR_INTERNAL_001",
                    "message": "Internal server error",
                    "details": {}
                }
            }
        )
