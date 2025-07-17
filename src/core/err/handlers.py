"""Exception handlers."""

import traceback

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger  # type: ignore
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """
    Handle HTTP exceptions.

    Args:
        request: FastAPI request
        exc: HTTP exception

    Returns:
        JSON response with error details
    """
    # Log the HTTP exception
    logger.error(
        f"[HTTP ERROR] Status: {exc.status_code} | Detail: {exc.detail} | URL: {request.url.path}"
    )

    if exc.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": "Internal Server Error", "status_code": exc.status_code},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle validation exceptions.

    Args:
        request: FastAPI request
        exc: Validation exception

    Returns:
        JSON response with error details
    """
    # Log the validation error
    error_details = exc.errors()
    logger.error(f"Validation Error on {request.url.path}: {error_details}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": error_details,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        },
    )


async def internal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle internal server errors.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON response with error details
    """
    # Get the exception traceback
    error_details = traceback.format_exception(type(exc), exc, exc.__traceback__)
    error_message = str(exc)

    # Log the error with traceback and any custom attributes
    custom_code = getattr(exc, "code", None)
    custom_detail = getattr(exc, "detail", None)
    logger.error(
        f"Internal Server Error on {request.url.path}: {error_message}\n"
        f"Traceback: {''.join(error_details)}"
        + (f"\nCustom code: {custom_code}" if custom_code else "")
        + (f"\nCustom detail: {custom_detail}" if custom_detail else "")
    )

    # Return a generic error message to the client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
    )