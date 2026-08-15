import logging

from fastapi import FastAPI

from app.api.convert import router as convert_router
from app.core.config import settings
from app.core.exceptions import (
    application_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import configure_logging
from app.core.middleware import (
    request_context_middleware,
)

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import PhotoModifierError

configure_logging()

logger = logging.getLogger(
    "photo_modifier"
)
logger.info(
    "Starting %s version %s in %s environment",
    settings.app_name,
    settings.app_version,
    settings.environment,
)

app = FastAPI(
    title=settings.app_name,
    description="Image processing and conversion API",
    version=settings.app_version,
)


app.middleware("http")(
    request_context_middleware
)


app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    Exception,
    unhandled_exception_handler,
)


app.add_exception_handler(
    401,
    http_exception_handler,
)

app.add_exception_handler(
    403,
    http_exception_handler,
)

app.add_exception_handler(
    404,
    http_exception_handler,
)

app.add_exception_handler(
    413,
    http_exception_handler,
)

app.add_exception_handler(
    415,
    http_exception_handler,
)

app.add_exception_handler(
    429,
    http_exception_handler,
)

app.add_exception_handler(
    PhotoModifierError,
    application_exception_handler,
)

app.include_router(
    convert_router
)


@app.get(
    "/health",
    tags=["System"],
)
async def health_check():

    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@app.get(
    "/ready",
    tags=["System"],
)
async def readiness_check():

    return {
        "status": "ready",
        "service": settings.app_name,
        "version": settings.app_version,
    }