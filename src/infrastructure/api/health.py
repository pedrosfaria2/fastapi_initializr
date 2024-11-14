from fastapi import APIRouter, status
import platform
import sys
import psutil
import time
from datetime import datetime

from src.infrastructure.config.settings import settings
from src.infrastructure.schemas.health import (
    HealthResponse,
    SystemInfo,
    PythonInfo,
    MemoryInfo,
)


class HealthAPI:
    def __init__(self, app):
        self.router = APIRouter()
        self.start_time = time.time()
        self._configure_routes()
        app.include_router(self.router)

    def _configure_routes(self):
        @self.router.get(
            "/health",
            response_model=HealthResponse,
            status_code=status.HTTP_200_OK,
            tags=["Health"],
            summary="Check service health",
            description="Returns detailed health information about the service",
        )
        async def health_check():
            return HealthResponse(
                status="healthy",
                environment=settings.ENVIRONMENT,
                version=settings.APP_VERSION,
                timestamp=datetime.utcnow().isoformat(),
                uptime=time.time() - self.start_time,
                python_info=PythonInfo(
                    version=sys.version,
                    implementation=platform.python_implementation(),
                    compiler=platform.python_compiler(),
                ),
                system_info=SystemInfo(
                    platform=platform.platform(),
                    architecture=platform.machine(),
                    processor=platform.processor() or "Unknown",
                    cpu_count=psutil.cpu_count(),
                    cpu_usage=psutil.cpu_percent(interval=0.1),
                ),
                memory_usage=MemoryInfo(
                    total=psutil.virtual_memory().total,
                    available=psutil.virtual_memory().available,
                    used_percent=psutil.virtual_memory().percent,
                ),
            )
