import logging
import time
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request pathways, processing times, and response statuses."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.perf_counter()

        # Extract metadata
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"

        logger.info(f"Incoming request: {method} {path} from client: {client_host}")

        try:
            response = await call_next(request)
        except Exception as e:
            process_time = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Unhandled exception during {method} {path}: {str(e)} "
                f"| Processed in: {process_time:.2f}ms",
                exc_info=True,
            )
            # Re-raise to let custom exception handlers resolve it
            raise e

        process_time = (time.perf_counter() - start_time) * 1000

        # Add latency header
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"

        # Log resolution
        logger.info(
            f"Completed request: {method} {path} with status: {response.status_code} "
            f"| Processed in: {process_time:.2f}ms"
        )

        return response
