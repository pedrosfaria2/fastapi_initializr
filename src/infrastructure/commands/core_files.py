from pathlib import Path
from typing import Dict, Any
from loguru import logger
from src.domain.commands.base import ProjectCommand
from src.domain.entities.command_result import CommandResult

from src.domain.entities.project import Project
from src.domain.repositories.template_repository import TemplateRepository
from src.infrastructure.enumerators.command_priority import CommandPriority


class CoreFilesCommand(ProjectCommand):
    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository

    @property
    def name(self) -> str:
        return "core_files"

    @property
    def priority(self) -> CommandPriority:
        return CommandPriority.HIGH

    @property
    def template_files(self) -> Dict[str, str]:
        return {
            "main.py": "minimal/main.py.jinja",
            ".gitignore": "minimal/gitignore.jinja",
        }

    async def validate(self, project: Project, context: Dict[str, Any]) -> bool:
        logger.debug(f"Validating {self.name} command")
        try:
            for _, template_path in self.template_files.items():
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
            for dest_path, template_path in self.template_files.items():
                template = self.template_repository.get_template_content(template_path)
                content = template.render(**context)
                file_path = output_path.joinpath(dest_path)
                file_path.write_text(content)
                changes[str(file_path)] = None
                logger.debug(f"Created file: {file_path}")

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
