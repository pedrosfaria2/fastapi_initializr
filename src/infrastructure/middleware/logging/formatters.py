from typing import Dict, Any
import json
from loguru import logger


class LogFormatter:
    @staticmethod
    def format_log(data: Dict[str, Any]) -> str:
        try:
            return json.dumps(data, separators=(",", ":"))
        except Exception as e:
            logger.error(f"Failed to format log data: {str(e)}")
            return str(data)
