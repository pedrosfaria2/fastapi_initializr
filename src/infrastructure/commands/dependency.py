from pathlib import Path
from typing import Dict, Any
from loguru import logger
from src.domain.commands.base import ProjectCommand
from src.domain.entities.command_result import CommandResult
from src.domain.entities.project import Project
from src.domain.repositories.template_repository import TemplateRepository
from src.infrastructure.enumerators.command_priority import CommandPriority
from src.infrastructure.enumerators.dependency_manager import DependencyManager
from src.infrastructure.exceptions.command_execution import CommandValidationError


class DependencyManagementCommand(ProjectCommand):
    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository

    @property
    def name(self) -> str:
        return "dependency_management"

    @property
    def priority(self) -> CommandPriority:
        return CommandPriority.HIGH

    @property
    def template_files(self) -> Dict[str, str]:
        return {
            "requirements.txt": "dependency/requirements.txt.jinja",
            "pyproject.toml": "dependency/pyproject.toml.jinja",
        }

    @staticmethod
    def _get_dependency_files(dependency_manager: str) -> Dict[str, str]:
        files = {"requirements.txt": "dependency/requirements.txt.jinja"}

        if dependency_manager == DependencyManager.POETRY:
            files.update(
                {
                    "pyproject.toml": "dependency/pyproject.toml.jinja",
                }
            )
        return files

    @staticmethod
    def _get_utils_dependencies(project: Project) -> list[str]:
        """Return a list of utility dependencies based on project options."""
        dependency_map = {
            "include_black": "black",
            "include_flake8": "flake8",
            "include_pre_commit": "pre-commit",
            "include_conventional_commit": "commitizen",
        }
        return [
            dep for option, dep in dependency_map.items() if getattr(project, option)
        ]

    async def validate(self, project: Project, context: Dict[str, Any]) -> bool:
        logger.debug(f"Validating {self.name} command")
        try:
            dependency_manager = context.get(
                "dependency_manager", DependencyManager.PIP
            )
            template_files = self._get_dependency_files(dependency_manager)

            for template_path in template_files.values():
                try:
                    self.template_repository.get_template_content(template_path)
                except Exception as e:
                    logger.error(f"Template {template_path} not found")
                    raise CommandValidationError(
                        f"Template {template_path} not found",
                        self.name,
                        details={"template_path": template_path},
                        original_error=e,
                    )
            return True
        except CommandValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected validation error: {str(e)}")
            raise CommandValidationError(
                str(e), self.name, details={"error": str(e)}, original_error=e
            )

    async def execute(
        self, project: Project, context: Dict[str, Any], output_path: Path
    ) -> CommandResult:
        logger.info(f"Executing {self.name} command")
        changes = {}

        try:
            utils_dependencies = self._get_utils_dependencies(project)
            context["utils_dependencies"] = utils_dependencies

            dependency_manager = context.get(
                "dependency_manager", DependencyManager.PIP
            )
            template_files = self._get_dependency_files(dependency_manager)

            for dest_path, template_path in template_files.items():
                template = self.template_repository.get_template_content(template_path)
                content = template.render(**context)
                file_path = output_path / dest_path
                file_path.write_text(content)
                changes[str(file_path)] = None
                logger.debug(f"Created file: {file_path} for {dependency_manager}")

            return CommandResult(success=True, changes=changes)

        except Exception as e:
            logger.error(f"Execution failed for {self.name}: {str(e)}")
            return CommandResult(success=False, changes=changes, error=str(e))

    async def rollback(
        self, project: Project, context: Dict[str, Any], changes: Dict[str, Any]
    ) -> None:
        logger.info(f"Rolling back {self.name} command")
        for file_path in changes.keys():
            try:
                Path(file_path).unlink(missing_ok=True)
                logger.debug(f"Removed file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to rollback {file_path}: {str(e)}")
