from src.domain.entities.project import Project
from src.domain.services.project_generator import ProjectGenerator
from src.infrastructure.schemas.project import ProjectSchema
import tempfile
from pathlib import Path


class ProjectService:
    def __init__(self, project_generator: ProjectGenerator):
        self.project_generator = project_generator

    async def create_project(self, project_schema: ProjectSchema) -> bytes:
        project = Project(
            name=project_schema.project_name,
            description=project_schema.description,
            template_type=project_schema.template_type,
            python_version=project_schema.python_version,
            author=project_schema.author,
            dependency_manager=project_schema.dependency_manager,
            dependencies={
                "fastapi": project_schema.fastapi_version,
                "uvicorn": project_schema.uvicorn_version,
            },
            include_dockerfile=project_schema.include_dockerfile,
            include_docker_compose=project_schema.include_docker_compose,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            return await self.project_generator.generate(project, Path(temp_dir))
