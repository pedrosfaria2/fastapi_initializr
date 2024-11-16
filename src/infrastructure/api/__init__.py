from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.api.health import HealthAPI
from src.infrastructure.api.generator import GeneratorAPI
from src.infrastructure.config.settings import settings
from src.infrastructure.middleware.logging.request_logging_middleware import RequestLoggingMiddleware
from src.infrastructure.middleware.rate_limiting.middleware import RateLimitingMiddleware


class APIBuilder:
    def __init__(self, app: FastAPI):
        self.app = app
        self._configure_middlewares()
        self._configure_routes()

    def _configure_middlewares(self):

        self.app.add_middleware(
            RateLimitingMiddleware,
            requests_limit=100,
            window_seconds=60,
            exclude_paths={"/health", "/metrics"},
        )

        self.app.add_middleware(
            RequestLoggingMiddleware,
            exclude_paths={"/health"},
            log_request_body=True,
            log_response_body=True,
            mask_sensitive_data=True,
            include_timing=True,
        )

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _configure_routes(self):
        HealthAPI(self.app)
        GeneratorAPI(self.app)

    @classmethod
    def create(cls) -> FastAPI:
        app = FastAPI(
            title=settings.APP_NAME,
            description="FastAPI project generator",
            version="0.1.0",
            docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
            redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        )
        return cls(app).app
