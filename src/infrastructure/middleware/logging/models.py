from dataclasses import dataclass


@dataclass
class RequestTiming:
    start_time: float
    end_time: float = 0.0

    @property
    def duration_ms(self) -> float:
        return round((self.end_time - self.start_time) * 1000, 2)
