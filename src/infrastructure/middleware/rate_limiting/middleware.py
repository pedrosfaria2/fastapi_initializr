from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from loguru import logger

from .store import InMemoryStore
from ..logging.base import BaseCustomMiddleware


class RateLimitExceeded(Exception):
    pass


class RateLimitingMiddleware(BaseCustomMiddleware):
    def __init__(
        self,
        app,
        *,
        requests_limit: int = 100,
        window_seconds: int = 60,
        exclude_paths: set[str] = None,
    ):
        super().__init__(app)
        self.store = InMemoryStore()
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.exclude_paths = exclude_paths or set()

    @staticmethod
    def _get_client_key(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _should_skip_rate_limiting(self, request: Request) -> bool:
        return request.url.path in self.exclude_paths

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if self._should_skip_rate_limiting(request):
            return await call_next(request)

        client_key = self._get_client_key(request)

        requests_count, time_until_reset = self.store.get_requests_count(
            client_key, self.window_seconds
        )

        self.store.add_request(client_key)

        if requests_count >= self.requests_limit:
            logger.warning(
                f"Rate limit exceeded for client {client_key}. "
                f"Count: {requests_count}, Limit: {self.requests_limit}"
            )
            return JSONResponse(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": (
                        f"Too many requests. Please try again in "
                        f"{time_until_reset:.1f} seconds."
                    ),
                    "reset_in_seconds": round(time_until_reset, 1),
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(round(time_until_reset)),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_limit)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_limit - requests_count - 1
        )
        response.headers["X-RateLimit-Reset"] = str(round(time_until_reset))

        return response
