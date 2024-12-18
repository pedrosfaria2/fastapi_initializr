from pathlib import Path
from typing import Dict, Any
from loguru import logger
from src.domain.commands.base import ProjectCommand
from src.domain.entities.command_result import CommandResult
from src.domain.entities.project import Project
from src.domain.repositories.template_repository import TemplateRepository

from src.infrastructure.enumerators.command_priority import CommandPriority
from src.infrastructure.enumerators.dependency_manager import DependencyManager


class DocumentationCommand(ProjectCommand):
    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository

    @property
    def name(self) -> str:
        return "documentation"

    @property
    def priority(self) -> CommandPriority:
        return CommandPriority.LOW

    @property
    def template_files(self) -> Dict[str, str]:
        return {
            "README.pip.md": "readme/README.pip.jinja",
            "README.poetry.md": "readme/README.poetry.jinja",
        }

    @staticmethod
    def _get_readme_template(dependency_manager: DependencyManager) -> str:
        return (
            "readme/README.poetry.jinja"
            if dependency_manager == DependencyManager.POETRY
            else "readme/README.pip.jinja"
        )

    async def validate(self, project: Project, context: Dict[str, Any]) -> bool:
        logger.debug(f"Validating {self.name} command")
        try:
            dependency_manager = DependencyManager(
                context.get("dependency_manager", DependencyManager.PIP)
            )
            template_path = self._get_readme_template(dependency_manager)
            self.template_repository.get_template_content(template_path)
            return True
        except Exception as e:
            logger.error(f"Validation failed for {self.name}: {str(e)}")
            return False

    async def execute(
        self, project: Project, context: Dict[str, Any], output_path: Path
    ) -> CommandResult:
        logger.info(f"Executing {self.name} command")
        changes = {}
        try:
            dependency_manager = DependencyManager(
                context.get("dependency_manager", DependencyManager.PIP)
            )
            template_path = self._get_readme_template(dependency_manager)
            template = self.template_repository.get_template_content(template_path)
            content = template.render(**context)

            file_path = output_path / "README.md"
            file_path.write_text(content)
            changes[str(file_path)] = None
            logger.debug(f"Created README.md using {dependency_manager.value} template")

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
