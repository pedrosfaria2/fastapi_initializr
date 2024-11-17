from src.domain.entities.project import Project
from src.domain.services.project_generator import ProjectGenerator
from src.infrastructure.schemas.project import ProjectSchema
import tempfile
from pathlib import Path


class ProjectService:
    def __init__(self, project_generator: ProjectGenerator):
        self.project_generator = project_generator

    def create_project(self, project_dto: ProjectSchema) -> bytes:
        project = Project(
            name=project_dto.project_name,
            description=project_dto.description,
            template_type=project_dto.template_type,
            python_version=project_dto.python_version,
            author=project_dto.author,
            dependencies={
                "fastapi": project_dto.fastapi_version,
                "uvicorn": project_dto.uvicorn_version,
            },
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            return self.project_generator.generate(project, Path(temp_dir))
