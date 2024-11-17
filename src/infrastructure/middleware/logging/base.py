from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class BaseCustomMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
