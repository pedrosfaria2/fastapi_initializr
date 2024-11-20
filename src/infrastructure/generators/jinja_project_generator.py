from pathlib import Path
import io
from zipfile import ZipFile
from typing import List, Tuple, Dict, Any
from loguru import logger

from src.domain.commands.base import ProjectCommand
from src.domain.entities.command_result import CommandResult
from src.domain.repositories.template_repository import TemplateRepository
from src.domain.services.project_generator import ProjectGenerator
from src.domain.commands.registry import CommandRegistry
from src.domain.entities.project import Project
from src.infrastructure.commands.core_files import CoreFilesCommand
from src.infrastructure.commands.dependency import DependencyManagementCommand
from src.infrastructure.commands.docker import DockerCommand
from src.infrastructure.commands.documentation import DocumentationCommand
from src.infrastructure.exceptions.command_execution import (
    CommandValidationError,
    CommandExecutionError,
)


class JinjaProjectGenerator(ProjectGenerator):
    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository
        self.registry = CommandRegistry()
        self._register_commands()

    def _register_commands(self):
        logger.info("Registering project commands")

        core_files = CoreFilesCommand(template_repository=self.template_repository)
        docker = DockerCommand(template_repository=self.template_repository)
        documentation = DocumentationCommand(
            template_repository=self.template_repository
        )
        dependency_manager = DependencyManagementCommand(
            template_repository=self.template_repository
        )

        self.registry.register(core_files)
        self.registry.register(docker)
        self.registry.register(documentation)
        self.registry.register(dependency_manager)

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
            "dependency_manager": project.dependency_manager,
        }

    async def _execute_commands(
        self, project: Project, context: Dict[str, Any], output_path: Path
    ) -> None:
        executed_commands: List[Tuple[ProjectCommand, CommandResult]] = []

        try:
            commands = self.registry.get_all_commands()

            logger.info("Validating all commands")
            for command in commands:
                if not await command.validate(project, context):
                    raise CommandValidationError(
                        f"Validation failed for command: {command.name}"
                    )

            logger.info("Executing commands in priority order")
            for command in commands:
                result = await command.execute(project, context, output_path)
                executed_commands.append((command, result))

                if not result.success:
                    raise CommandExecutionError(
                        f"Command failed: {command.name} - {result.error}"
                    )

        except Exception as exc:
            logger.error(f"Command execution failed: {str(exc)}")
            logger.info("Starting rollback process")
            for command, result in reversed(executed_commands):
                await command.rollback(project, context, result.changes)
            raise exc

    async def generate(self, project: Project, output_path: Path) -> bytes:
        temp_dir = None
        try:
            logger.info(f"Starting project generation: {project.name}")
            ctx = self._create_context(project)
            temp_dir = output_path / project.name
            temp_dir.mkdir(exist_ok=True)

            await self._execute_commands(project, ctx, temp_dir)

            logger.info("Creating ZIP archive")
            zip_buffer = io.BytesIO()
            with ZipFile(zip_buffer, "w") as zip_file:
                for file_path in temp_dir.rglob("*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(temp_dir)
                        zip_file.write(file_path, str(relative_path))
                        logger.debug(f"Added to ZIP: {relative_path}")

            zip_buffer.seek(0)
            logger.info("Project generation completed successfully")
            return zip_buffer.getvalue()

        except Exception as exc:
            logger.error(f"Project generation failed: {str(exc)}")
            raise RuntimeError(f"Failed to generate project: {str(exc)}")
        finally:
            if temp_dir:
                try:
                    import shutil

                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as cleanup_error:
                    logger.warning(
                        f"Failed to cleanup temporary files: {str(cleanup_error)}"
                    )
