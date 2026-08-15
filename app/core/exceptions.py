import logging

from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


from app.schemas.errors import (
    ErrorBody,
    ErrorResponse,
)

from app.core.errors import PhotoModifierError

logger = logging.getLogger(
    "photo_modifier.errors"
)

def _request_id(
    
    request: Request,
) -> str:
    return getattr(
        request.state,
        "request_id",
        "unknown",
    )


def _response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: Any | None = None,
) -> JSONResponse:

    request_id = _request_id(request)

    payload = ErrorResponse(
        error=ErrorBody(
            code=code,
            message=message,
            details=details,
        ),
        request_id=request_id,
    )

    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(
            mode="json",
        ),
        headers={
            "X-Request-ID": request_id,
        },
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:

    status_code = exc.status_code

    error_mapping = {
        400: (
            "invalid_request",
            "The request could not be processed.",
        ),
        401: (
            "unauthorized",
            "Authentication is required.",
        ),
        403: (
            "forbidden",
            "You are not allowed to perform this operation.",
        ),
        404: (
            "not_found",
            "The requested resource was not found.",
        ),
        413: (
            "file_too_large",
            "The uploaded file is too large.",
        ),
        415: (
            "unsupported_media_type",
            "The uploaded media type is not supported.",
        ),
        422: (
            "validation_error",
            "The request contains invalid parameters.",
        ),
        429: (
            "rate_limit_exceeded",
            "Too many requests.",
        ),
        500: (
            "internal_server_error",
            "An unexpected server error occurred.",
        ),
    }

    code, default_message = error_mapping.get(
        status_code,
        (
            "request_error",
            "The request could not be processed.",
        ),
    )

    if isinstance(exc.detail, str):
        message = exc.detail
        details = None
    else:
        message = default_message
        details = exc.detail

    return _response(
        request=request,
        status_code=status_code,
        code=code,
        message=message,
        details=details,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:

    return _response(
        request=request,
        status_code=422,
        code="validation_error",
        message="Request validation failed.",
        details=exc.errors(),
    )

async def application_exception_handler(
    request: Request,
    exc: PhotoModifierError,
) -> JSONResponse:

    return _response(
        request=request,
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )

    
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:

    logger.exception(
        "Unhandled application exception request_id=%s",
        _request_id(request),
        exc_info=exc,
    )

    return _response(
        request=request,
        status_code=500,
        code="internal_server_error",
        message="An unexpected server error occurred.",
    )
