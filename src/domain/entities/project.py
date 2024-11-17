from dataclasses import dataclass
from typing import Optional
from enum import Enum


class TemplateType(str, Enum):
    MINIMAL = "minimal"
    BASIC = "basic"
    FULL = "full"


@dataclass
class Project:
    name: str
    description: str
    template_type: TemplateType
    python_version: str
    author: Optional[str]
    dependencies: dict[str, str]
