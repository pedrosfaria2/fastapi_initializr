from dataclasses import dataclass
from typing import Optional
from src.infrastructure.enumerators.template_type import TemplateType


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
    include_black: bool = False
    include_conventional_commit: bool = False
    include_pre_commit: bool = False
    include_flake8: bool = False
