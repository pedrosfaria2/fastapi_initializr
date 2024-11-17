from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint
from loguru import logger
from contextlib import asynccontextmanager
import time

from .base import BaseCustomMiddleware
from .constants import (
    DEFAULT_EXCLUDED_PATHS,
    DEFAULT_EXCLUDED_METHODS,
    nullcontext,
    LogLevel,
)
from .request_logger import RequestLogger
from .response_logger import ResponseLogger


class RequestLoggingMiddleware(BaseCustomMiddleware):
    def __init__(
        self,
        app,
        *,
        exclude_paths: set[str] = None,
        exclude_methods: set[str] = None,
        log_request_body: bool = True,
        log_response_body: bool = True,
        mask_sensitive_data: bool = True,
        include_timing: bool = True,
    ):
        super().__init__(app)
        self.duration_ms = None
        self.exclude_paths = exclude_paths or DEFAULT_EXCLUDED_PATHS
        self.exclude_methods = exclude_methods or DEFAULT_EXCLUDED_METHODS
        self.include_timing = include_timing
        self.request_logger = RequestLogger(
            log_request_body=log_request_body,
            mask_sensitive_data=mask_sensitive_data,
        )
        self.response_logger = ResponseLogger(
            log_response_body=log_response_body,
            mask_sensitive_data=mask_sensitive_data,
        )

    @asynccontextmanager
    async def timing_context(self):
        start = time.time()
        try:
            yield
        finally:
            self.duration_ms = round((time.time() - start) * 1000, 2)

    def _should_skip_logging(self, request: Request) -> bool:
        return (
            request.url.path in self.exclude_paths
            or request.method in self.exclude_methods
        )

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if self._should_skip_logging(request):
            return await call_next(request)

        self.duration_ms = None
        timing_ctx = self.timing_context() if self.include_timing else nullcontext()

        log_data, request_id = await self.request_logger.build_log(request)

        async with timing_ctx:
            try:
                response = await call_next(request)
                status_code = response.status_code
            except Exception as exc:
                logger.error(f"Request {request_id}: Unhandled exception - {str(exc)}")
                raise
            finally:
                log_data.update(self.response_logger.build_log(response, status_code))
                if self.include_timing:
                    log_data["duration_ms"] = self.duration_ms

                log_level = LogLevel.from_status_code(status_code)
                logger.log(log_level, log_data)

        return response
