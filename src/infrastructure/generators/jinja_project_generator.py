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
from src.infrastructure.commands.basic_template import BasicTemplateCommand
from src.infrastructure.commands.minimal_template import MinimalTemplateCommand
from src.infrastructure.commands.dependency import DependencyManagementCommand
from src.infrastructure.commands.docker import DockerCommand
from src.infrastructure.commands.documentation import DocumentationCommand
from src.infrastructure.commands.utils import UtilsCommand
from src.infrastructure.enumerators.template_type import TemplateType
from src.infrastructure.exceptions.command_execution import (
    CommandValidationError,
    CommandExecutionError,
)


class JinjaProjectGenerator(ProjectGenerator):
    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository
        self.registry = CommandRegistry()
        self.template_commands = {
            TemplateType.MINIMAL: MinimalTemplateCommand(
                template_repository=self.template_repository
            ),
            TemplateType.BASIC: BasicTemplateCommand(
                template_repository=self.template_repository
            ),
        }

    @staticmethod
    def _create_context(project: Project) -> Dict[str, Any]:
        dependency_map = JinjaProjectGenerator._create_dependency_map()
        utils_dependencies = [
            dependency
            for option, dependency in dependency_map.items()
            if getattr(project, option, False)
        ]
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
            "utils_dependencies": utils_dependencies,
        }

    @staticmethod
    def _create_dependency_map() -> Dict[str, str]:
        return {
            "include_black": "black",
            "include_flake8": "flake8",
            "include_pre_commit": "pre-commit",
            "include_conventional_commit": "commitizen",
        }

    def _register_commands(self, project: Project) -> None:
        logger.info("Registering project commands")
        self.registry = CommandRegistry()
        template_command = self.template_commands.get(project.template_type)
        if not template_command:
            raise ValueError(f"Unknown template type: {project.template_type}")
        commands = [
            template_command,
            DockerCommand,
            DocumentationCommand,
            DependencyManagementCommand,
            UtilsCommand,
        ]
        for command in commands:
            self.registry.register(
                command(template_repository=self.template_repository)
            )

    async def _execute_commands(
        self, project: Project, context: Dict[str, Any], output_path: Path
    ) -> None:
        executed_commands: List[Tuple[ProjectCommand, CommandResult]] = []
        try:
            commands = self.registry.get_all_commands()
            logger.info("Validating all commands")
            failed_validations = [
                cmd for cmd in commands if not await cmd.validate(project, context)
            ]
            if failed_validations:
                invalid_command_names = ", ".join(
                    cmd.name for cmd in failed_validations
                )
                raise CommandValidationError(
                    f"Validation failed for commands: {invalid_command_names}",
                    invalid_command_names,
                )

            logger.info("Executing commands in priority order")
            execute_command = self._execute_single_command
            executed_commands = [
                await execute_command(cmd, project, context, output_path)
                for cmd in commands
            ]

        except Exception as exc:
            logger.error(f"Command execution failed: {str(exc)}")
            logger.info("Starting rollback process")
            await self._rollback_commands(project, context, executed_commands)
            raise exc

    @staticmethod
    async def _execute_single_command(
        command: ProjectCommand,
        project: Project,
        context: Dict[str, Any],
        output_path: Path,
    ) -> Tuple[ProjectCommand, CommandResult]:
        result = await command.execute(project, context, output_path)
        if not result.success:
            raise CommandExecutionError(
                f"Command failed: {command.name} - {result.error}",
                command.name,
                {"error": result.error},
            )
        return command, result

    @staticmethod
    async def _rollback_commands(
        project: Project,
        context: Dict[str, Any],
        executed_commands: List[Tuple[ProjectCommand, CommandResult]],
    ) -> None:
        for command, result in reversed(executed_commands):
            try:
                await command.rollback(project, context, result.changes)
            except Exception as rollback_error:
                logger.error(
                    f"Failed to rollback command {command.name}: {str(rollback_error)}"
                )

    async def generate(self, project: Project, output_path: Path) -> bytes:
        temp_dir = None
        try:
            logger.info(f"Starting project generation: {project.name}")
            context = self._create_context(project)
            temp_dir = self._prepare_temp_dir(output_path, project.name)
            self._register_commands(project)
            await self._execute_commands(project, context, temp_dir)
            return self._prepare_zip_buffer(temp_dir)
        except Exception as exc:
            logger.error(f"Project generation failed: {str(exc)}")
            raise RuntimeError(f"Failed to generate project: {str(exc)}")
        finally:
            if temp_dir and temp_dir.exists():
                try:
                    import shutil

                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as cleanup_error:
                    logger.warning(
                        f"Failed to cleanup temporary files: {str(cleanup_error)}"
                    )

    @staticmethod
    def _prepare_temp_dir(output_path: Path, project_name: str) -> Path:
        temp_dir = output_path / project_name
        temp_dir.mkdir(exist_ok=True)
        return temp_dir

    @staticmethod
    def _prepare_zip_buffer(temp_dir: Path) -> bytes:
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, "w") as zip_file:
            file_paths = [
                file_path for file_path in temp_dir.rglob("*") if file_path.is_file()
            ]
            for file_path in file_paths:
                relative_path = file_path.relative_to(temp_dir)
                zip_file.write(file_path, str(relative_path))
                logger.debug(f"Added to ZIP: {relative_path}")
        zip_buffer.seek(0)
        logger.info("Project generation completed successfully")
        return zip_buffer.getvalue()
