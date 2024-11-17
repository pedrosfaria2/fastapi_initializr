from typing import Any, Dict, Optional


class RequestContext:
    def __init__(self, request_id: str, correlation_id: Optional[str] = None):
        self.request_id = request_id
        self.correlation_id = correlation_id
        self.extras: Dict[str, Any] = {}

    def add_extra(self, key: str, value: Any) -> None:
        self.extras[key] = value
