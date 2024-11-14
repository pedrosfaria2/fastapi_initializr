import json

from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint
from starlette.types import ASGIApp
from loguru import logger
from datetime import datetime, UTC
from http import HTTPStatus
import traceback
from typing import Any, Dict
from json.decoder import JSONDecodeError
import uuid

from src.infrastructure.middleware.base import BaseCustomMiddleware
from src.infrastructure.middleware.logging.constants import (
    DEFAULT_EXCLUDED_PATHS,
    DEFAULT_EXCLUDED_METHODS,
    DEFAULT_SENSITIVE_HEADERS,
    LogLevel,
)
from src.infrastructure.middleware.logging.context import RequestContext
from src.infrastructure.middleware.logging.formatters import LogFormatter
from src.infrastructure.middleware.logging.utils import (
    request_timing,
    get_client_ip,
    mask_sensitive_data,
)


class RequestLoggingMiddleware(BaseCustomMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        *,
        exclude_paths: set[str] = None,
        exclude_methods: set[str] = None,
        log_request_body: bool = True,
        log_response_body: bool = True,
        sensitive_headers: set[str] = None,
        mask_sensitive_data: bool = True,
        log_level: str = "INFO",
        include_timing: bool = True,
        include_request_id: bool = True,
        request_id_header: str = "X-Request-ID",
        correlation_id_header: str = "X-Correlation-ID",
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or DEFAULT_EXCLUDED_PATHS
        self.exclude_methods = exclude_methods or DEFAULT_EXCLUDED_METHODS
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.sensitive_headers = sensitive_headers or DEFAULT_SENSITIVE_HEADERS
        self.mask_sensitive_data = mask_sensitive_data
        self.log_level = log_level
        self.include_timing = include_timing
        self.include_request_id = include_request_id
        self.request_id_header = request_id_header
        self.correlation_id_header = correlation_id_header

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if self._should_skip_logging(request):
            return await call_next(request)

        context = RequestContext(
            request_id=self._get_or_generate_request_id(request),
            correlation_id=request.headers.get(self.correlation_id_header),
        )

        async with request_timing() as timing:
            log_data = await self._build_request_log(request, context)
            response = None
            status_code = 500

            try:
                response = await call_next(request)
                status_code = response.status_code
                return response
            except Exception as exc:
                logger.error(f"Unhandled exception: {str(exc)}")
                logger.error(traceback.format_exc())
                raise
            finally:
                if self.include_timing:
                    context.add_extra("duration_ms", timing.duration_ms)
                if response:
                    log_data.update(
                        await self._build_response_log(response, status_code)
                    )
                log_data.update(context.extras)
                self._log_request(log_data, status_code)

    def _should_skip_logging(self, request: Request) -> bool:
        return (
            request.url.path in self.exclude_paths
            or request.method in self.exclude_methods
        )

    def _get_or_generate_request_id(self, request: Request) -> str:
        if self.include_request_id:
            return request.headers.get(self.request_id_header) or str(uuid.uuid4())
        return ""

    async def _build_request_log(
        self, request: Request, context: RequestContext
    ) -> Dict[str, Any]:
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "request_id": context.request_id,
            "correlation_id": context.correlation_id,
            "method": request.method,
            "url": str(request.url),
            "path_params": dict(request.path_params),
            "query_params": dict(request.query_params),
            "client_ip": get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
        }

        headers = dict(request.headers)
        if self.mask_sensitive_data:
            headers = mask_sensitive_data(headers, self.sensitive_headers)
        log_data["headers"] = headers

        if self.log_request_body:
            try:
                body = await self._get_request_body(request)
                if self.mask_sensitive_data:
                    body = mask_sensitive_data(body, self.sensitive_headers)
                log_data["body"] = body
            except (UnicodeDecodeError, JSONDecodeError) as e:
                logger.warning(f"Failed to decode request body: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error reading request body: {str(e)}")

        return log_data

    async def _build_response_log(
        self, response: Response, status_code: int
    ) -> Dict[str, Any]:
        log_data = {
            "status_code": status_code,
            "status_phrase": HTTPStatus(status_code).phrase,
        }

        headers = dict(response.headers)
        if self.mask_sensitive_data:
            headers = mask_sensitive_data(headers, self.sensitive_headers)
        log_data["response_headers"] = headers

        if self.log_response_body and hasattr(response, "body"):
            try:
                body = response.body.decode()
                if self.mask_sensitive_data:
                    body = mask_sensitive_data(body, self.sensitive_headers)
                log_data["response_body"] = body
            except UnicodeDecodeError as e:
                logger.warning(f"Failed to decode response body: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error reading response body: {str(e)}")

        return log_data

    @staticmethod
    async def _get_request_body(request: Request) -> Any:
        if not hasattr(request, "body"):
            return None

        body = await request.body()

        try:
            return json.loads(body)
        except JSONDecodeError:
            return body.decode()
        except Exception as e:
            logger.error(f"Failed to process request body: {str(e)}")
            return str(body)

    @staticmethod
    def _log_request(log_data: Dict[str, Any], status_code: int) -> None:
        log_level = LogLevel.from_status_code(status_code)
        formatted_log = LogFormatter.format_log(log_data)
        logger.log(log_level, formatted_log)
