from typing import Dict, Tuple
from time import time
from collections import defaultdict


class InMemoryStore:
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)

    def add_request(self, key: str, timestamp: float = None) -> None:
        if timestamp is None:
            timestamp = time()
        self._requests[key].append(timestamp)

    def clean_old_requests(self, key: str, window: int) -> None:
        if key in self._requests:
            current_time = time()
            self._requests[key] = [
                ts for ts in self._requests[key] if current_time - ts < window
            ]

    def get_requests_count(self, key: str, window: int) -> Tuple[int, float]:
        self.clean_old_requests(key, window)

        if not self._requests[key]:
            return 0, 0

        current_time = time()
        oldest_timestamp = min(self._requests[key])
        time_until_reset = max(0, window - (current_time - oldest_timestamp))

        return len(self._requests[key]), time_until_reset
