from pydantic import BaseModel


class SystemInfo(BaseModel):
    platform: str
    architecture: str
    processor: str
    cpu_count: int
    cpu_usage: float


class PythonInfo(BaseModel):
    version: str
    implementation: str
    compiler: str


class MemoryInfo(BaseModel):
    total: int
    available: int
    used_percent: float


class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str
    timestamp: str
    uptime: float
    python_info: PythonInfo
    system_info: SystemInfo
    memory_usage: MemoryInfo

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "environment": "dev",
                "version": "0.1.0",
                "timestamp": "2024-02-14T12:00:00.000Z",
                "uptime": 1234.56,
                "python_info": {
                    "version": "3.10.0",
                    "implementation": "CPython",
                    "compiler": "GCC 9.3.0",
                },
                "system_info": {
                    "platform": "Linux-5.4.0-x86_64",
                    "architecture": "x86_64",
                    "processor": "Intel(R) Core(TM) i7",
                    "cpu_count": 8,
                    "cpu_usage": 45.2,
                },
                "memory_usage": {
                    "total": 16777216000,
                    "available": 8388608000,
                    "used_percent": 50.0,
                },
            }
        }
