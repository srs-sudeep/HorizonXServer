"""Error handling package."""

from src.core.err.handlers import (
    http_exception_handler,
    internal_exception_handler,
    validation_exception_handler,
)
from src.core.err.models import ErrorResponse

__all__ = [
    "ErrorResponse",
    "http_exception_handler",
    "internal_exception_handler",
    "validation_exception_handler",
    "setup_exception_handlers",
]


def setup_exception_handlers(app):
    """
    Set up exception handlers.

    Args:
        app: FastAPI application
    """
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException

    # Handle specific HTTP exceptions
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # Handle validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Handle all other unhandled exceptions
    app.add_exception_handler(Exception, internal_exception_handler)
