from pydantic import BaseModel, Field
from typing import Optional, List


class ProjectTemplate(BaseModel):
    id: str
    name: str
    description: str
    features: List[str] = []


class DatabaseConfig(BaseModel):
    type: str = Field(..., description="Database type (sqlite, postgres, mysql)")
    use_migrations: bool = Field(default=True, description="Include Alembic migrations")
    async_driver: bool = Field(default=False, description="Use async database driver")


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., description="Project name")
    description: Optional[str] = None
    template_id: str = Field(..., description="Template ID to use")
    python_version: str = Field(default="3.10", description="Python version")
    use_docker: bool = Field(default=True, description="Include Docker configuration")
    use_poetry: bool = Field(
        default=True, description="Use Poetry for dependency management"
    )
    database: Optional[DatabaseConfig] = None
    features: List[str] = Field(
        default_list=[], description="Additional features to include"
    )


class ProjectCreateResponse(BaseModel):
    project_id: str = Field(..., description="Generated project identifier")
    download_url: str = Field(..., description="URL to download the generated project")
