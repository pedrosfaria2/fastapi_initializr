from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class CommandResult:
    success: bool
    changes: Dict[str, Any]
    error: Optional[str] = None
