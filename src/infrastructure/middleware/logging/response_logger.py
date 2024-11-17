from fastapi import Response
from typing import Dict, Any
from http import HTTPStatus
from loguru import logger

from .utils import mask_sensitive_data
from .constants import DEFAULT_SENSITIVE_HEADERS


class ResponseLogger:
    def __init__(
        self,
        *,
        log_response_body: bool = True,
        sensitive_headers: set[str] = None,
        mask_sensitive_data: bool = True,
    ):
        self.log_response_body = log_response_body
        self.sensitive_headers = sensitive_headers or DEFAULT_SENSITIVE_HEADERS
        self.mask_sensitive_data = mask_sensitive_data

    def build_log(self, response: Response, status_code: int) -> Dict[str, Any]:
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
                logger.error(f"Failed to read response body: {str(e)}")

        return log_data
