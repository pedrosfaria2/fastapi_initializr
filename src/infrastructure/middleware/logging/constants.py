from enum import Enum
from contextlib import contextmanager


@contextmanager
def nullcontext():
    yield


class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

    @classmethod
    def from_status_code(cls, status_code: int) -> "LogLevel":
        if status_code >= 500:
            return cls.ERROR
        elif status_code >= 400:
            return cls.WARNING
        return cls.INFO


DEFAULT_EXCLUDED_PATHS = {"/health", "/metrics"}
DEFAULT_EXCLUDED_METHODS = {"OPTIONS"}
DEFAULT_SENSITIVE_HEADERS = {"authorization", "cookie", "x-api-key"}
