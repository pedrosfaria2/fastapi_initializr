from pathlib import Path
from typing import Dict, Any
from loguru import logger

from src.domain.commands.base import ProjectCommand
from src.domain.entities.command_result import CommandResult
from src.domain.entities.project import Project
from src.domain.repositories.template_repository import TemplateRepository
from src.infrastructure.enumerators.command_priority import CommandPriority
from src.infrastructure.exceptions.command_execution import CommandValidationError


class UtilsCommand(ProjectCommand):
    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository

    @property
    def name(self) -> str:
        return "utils"

    @property
    def priority(self) -> CommandPriority:
        return CommandPriority.MEDIUM

    @property
    def template_files(self) -> Dict[str, str]:
        return {
            ".pre-commit-config.yaml": "utils/pre-commit-config.yaml.jinja",
            ".flake8": "utils/flake8.jinja",
        }

    async def validate(self, project: Project, context: Dict[str, Any]) -> bool:
        logger.debug(f"Validating {self.name} command")
        try:
            for _, template_path in self.template_files.items():
                try:
                    self.template_repository.get_template_content(template_path)
                except Exception as e:
                    logger.error(f"Template {template_path} not found")
                    raise CommandValidationError(
                        message=f"Template {template_path} not found",
                        command_name=self.name,
                        details={"template_path": template_path},
                        original_error=e,
                    )
            return True
        except CommandValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected validation error: {str(e)}")
            raise CommandValidationError(
                message=str(e),
                command_name=self.name,
                details={"error": str(e)},
                original_error=e,
            )

    async def execute(
        self, project: Project, context: Dict[str, Any], output_path: Path
    ) -> CommandResult:
        if not (
            project.include_black
            or project.include_conventional_commit
            or project.include_pre_commit
            or project.include_flake8
        ):
            return CommandResult(success=True, changes={})

        logger.info(f"Executing {self.name} command")
        changes = {}
        try:
            for dest_path, template_path in self.template_files.items():
                template = self.template_repository.get_template_content(template_path)
                content = template.render(**context)
                file_path = output_path / dest_path
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
