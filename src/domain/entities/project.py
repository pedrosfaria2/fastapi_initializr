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
    include_dockerfile: bool = False
    include_docker_compose: bool = False
    dependency_manager: str = "pip"
