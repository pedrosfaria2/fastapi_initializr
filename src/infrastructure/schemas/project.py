from pydantic import BaseModel, Field
from src.infrastructure.enumerators.dependency_manager import DependencyManager
from src.infrastructure.enumerators.template_type import TemplateType


class ProjectSchema(BaseModel):
    project_name: str = Field(default="my_project_name", min_length=1, max_length=100)
    description: str = Field(default="A FastAPI application")
    template_type: TemplateType = Field(default=TemplateType.MINIMAL)
    python_version: str = Field(default="3.10")
    author: str = Field(default="Author <example@example.com>")
    dependency_manager: DependencyManager = Field(
        default=DependencyManager.PIP,
        description="Package manager to use (pip or poetry)",
    )
    fastapi_version: str = Field(default="0.100.0")
    uvicorn_version: str = Field(default="0.22.0")
    include_dockerfile: bool = Field(default=False)
    include_docker_compose: bool = Field(default=False)
    include_black: bool = Field(
        default=False, description="Include Black configuration"
    )
    include_conventional_commit: bool = Field(
        default=False, description="Include Conventional Commit configuration"
    )
    include_pre_commit: bool = Field(
        default=False, description="Include Pre-Commit configuration"
    )
    include_flake8: bool = Field(
        default=False, description="Include Flake8 configuration"
    )
