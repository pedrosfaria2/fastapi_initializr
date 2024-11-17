from fastapi import Request
from datetime import datetime, UTC
import uuid
from typing import Dict, Any
import json
from json.decoder import JSONDecodeError
from loguru import logger

from .utils import get_client_ip, mask_sensitive_data
from .constants import DEFAULT_SENSITIVE_HEADERS


class RequestLogger:
    def __init__(
        self,
        *,
        log_request_body: bool = True,
        sensitive_headers: set[str] = None,
        mask_sensitive_data: bool = True,
        request_id_header: str = "X-Request-ID",
        correlation_id_header: str = "X-Correlation-ID",
    ):
        self.log_request_body = log_request_body
        self.sensitive_headers = sensitive_headers or DEFAULT_SENSITIVE_HEADERS
        self.mask_sensitive_data = mask_sensitive_data
        self.request_id_header = request_id_header
        self.correlation_id_header = correlation_id_header

    def get_request_id(self, request: Request) -> str:
        return request.headers.get(self.request_id_header) or str(uuid.uuid4())

    async def build_log(self, request: Request) -> tuple[Dict[str, Any], str]:
        request_id = self.get_request_id(request)
        correlation_id = request.headers.get(self.correlation_id_header)

        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "request_id": request_id,
            "correlation_id": correlation_id,
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
            body = await self._get_request_body(request)
            if body is not None:
                if self.mask_sensitive_data:
                    body = mask_sensitive_data(body, self.sensitive_headers)
                log_data["body"] = body

        return log_data, request_id

    @staticmethod
    async def _get_request_body(request: Request) -> Any:
        if not hasattr(request, "body"):
            return None

        body = await request.body()
        if not body:
            return None

        try:
            return json.loads(body)
        except JSONDecodeError:
            try:
                return body.decode()
            except UnicodeDecodeError as e:
                logger.warning(f"Failed to decode request body: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"Failed to process request body: {str(e)}")
            return None
