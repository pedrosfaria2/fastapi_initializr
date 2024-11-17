from pathlib import Path
import io
from zipfile import ZipFile
from loguru import logger
from typing import List, Dict, Any
from src.domain.entities.project import Project
from src.domain.services.project_generator import ProjectGenerator
from src.domain.repositories.template_repository import TemplateRepository
from src.domain.commands.base import ProjectCommand

from ..commands.core_files import CoreFilesCommand
from ..commands.docker import DockerCommand
from ..commands.documentation import DocumentationCommand


class JinjaProjectGenerator(ProjectGenerator):
    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository
        self.commands: List[ProjectCommand] = [
            CoreFilesCommand(template_repository),
            DockerCommand(template_repository),
            DocumentationCommand(template_repository),
        ]

    @staticmethod
    def _create_context(project: Project) -> Dict[str, Any]:
        return {
            "project_name": project.name,
            "description": project.description,
            "python_version": project.python_version,
            "author": project.author,
            "fastapi_version": project.dependencies["fastapi"],
            "uvicorn_version": project.dependencies["uvicorn"],
            "include_dockerfile": project.include_dockerfile,
            "include_docker_compose": project.include_docker_compose,
        }

    def generate(self, project: Project, output_path: Path) -> bytes:
        try:
            context = self._create_context(project)
            temp_output = output_path / project.name
            temp_output.mkdir(exist_ok=True)

            for command in self.commands:
                try:
                    command.execute(project, context, temp_output)
                except Exception as e:
                    logger.error(
                        f"Command {command.__class__.__name__} failed: {str(e)}"
                    )
                    raise ValueError(f"Failed to execute {command.__class__.__name__}")

            zip_buffer = io.BytesIO()
            with ZipFile(zip_buffer, "w") as zip_file:
                for file_path in temp_output.rglob("*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(temp_output)
                        zip_file.write(file_path, str(relative_path))

            zip_buffer.seek(0)
            return zip_buffer.getvalue()

        except Exception as e:
            logger.error(f"Project generation failed: {str(e)}")
            raise RuntimeError(f"Failed to generate project: {str(e)}")
