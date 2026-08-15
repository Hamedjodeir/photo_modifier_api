import logging
import time
from uuid import uuid4

from fastapi import Request


logger = logging.getLogger(
    "photo_modifier.request"
)


async def request_context_middleware(
    request: Request,
    call_next,
):
    request_id = str(uuid4())

    request.state.request_id = request_id

    start_time = time.perf_counter()

    response = await call_next(
        request
    )

    duration_ms = (
        time.perf_counter() - start_time
    ) * 1000

    response.headers["X-Request-ID"] = (
        request_id
    )

    response.headers["X-Process-Time-Ms"] = (
        f"{duration_ms:.2f}"
    )

    logger.info(
        "%s %s completed status=%s duration_ms=%.2f request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
    )

    return response