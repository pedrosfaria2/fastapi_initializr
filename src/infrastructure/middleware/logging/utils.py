from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any
from fastapi import Request
import time
import json
from json.decoder import JSONDecodeError

from src.infrastructure.middleware.logging.models import RequestTiming


@asynccontextmanager
async def request_timing() -> AsyncGenerator[RequestTiming, None]:
    timing = RequestTiming(start_time=time.time())
    try:
        yield timing
    finally:
        timing.end_time = time.time()


def mask_sensitive_data(data: Any, sensitive_headers: set[str]) -> Any:
    if isinstance(data, dict):
        return {
            k: (
                "***MASKED***"
                if k.lower() in sensitive_headers
                else mask_sensitive_data(v, sensitive_headers)
            )
            for k, v in data.items()
        }
    if isinstance(data, str):
        try:
            json_data = json.loads(data)
            if isinstance(json_data, dict):
                return json.dumps(mask_sensitive_data(json_data, sensitive_headers))
        except JSONDecodeError:
            pass
    return data


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""
