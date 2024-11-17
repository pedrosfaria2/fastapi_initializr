from pydantic import BaseModel, Field
from src.domain.entities.project import TemplateType


class ProjectSchema(BaseModel):
    project_name: str = Field(default="my_project_name", min_length=1, max_length=100)
    description: str = Field(default="A FastAPI application")
    template_type: TemplateType = Field(default=TemplateType.MINIMAL)
    python_version: str = Field(default="3.10")
    author: str = Field(default="")
    fastapi_version: str = Field(default="0.100.0")
    uvicorn_version: str = Field(default="0.22.0")
    include_dockerfile: bool = Field(default=False)
    include_docker_compose: bool = Field(default=False)
