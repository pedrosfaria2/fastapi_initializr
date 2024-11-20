from pathlib import Path
from typing import Dict, Any, Set
from loguru import logger
from src.domain.commands.base import ProjectCommand
from src.domain.entities.command_result import CommandResult
from src.domain.entities.project import Project
from src.domain.repositories.template_repository import TemplateRepository
from src.infrastructure.enumerators.command_priority import CommandPriority


class BasicTemplateCommand(ProjectCommand):
    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository

    @property
    def name(self) -> str:
        return "basic_template"

    @property
    def priority(self) -> CommandPriority:
        return CommandPriority.HIGH

    @property
    def template_files(self) -> Dict[str, str]:
        return {
            "main.py": "basic/main.py.jinja",
            "app/routers/__init__.py": "basic/app/routers/__init__.py.jinja",
            "app/routers/example.py": "basic/app/routers/example.py.jinja",
            "app/services/example_service.py": "basic/app/services/example_service.py.jinja",
            "app/models/example_model.py": "basic/app/models/example_model.py.jinja",
            "app/db/connection.py": "basic/app/db/connection.py.jinja",
            "app/core/config.py": "basic/app/core/config.py.jinja",
        }

    @property
    def init_dirs(self) -> Set[str]:
        return {"app", "app/services", "app/models", "app/db", "app/core"}

    async def validate(self, project: Project, context: Dict[str, Any]) -> bool:
        logger.debug(f"Validating {self.name} command")
        try:
            for template_path in self.template_files.values():
                self.template_repository.get_template_content(template_path)

            self.template_repository.get_template_content("common/empty_init.py.jinja")

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
            empty_init = self.template_repository.get_template_content(
                "common/empty_init.py.jinja"
            )

            for dir_path in self.init_dirs:
                (output_path / dir_path).mkdir(parents=True, exist_ok=True)
                changes[f"dir:{dir_path}"] = None

                init_file = output_path / dir_path / "__init__.py"
                init_file.write_text(empty_init.render())
                changes[str(init_file)] = None

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
        for path_str in changes.keys():
            try:
                if path_str.startswith("dir:"):
                    dir_path = Path(path_str[4:])
                    try:
                        dir_path.rmdir()
                        logger.debug(f"Removed directory: {dir_path}")
                    except OSError:
                        logger.debug(
                            f"Directory not empty, skipping removal: {dir_path}"
                        )
                else:
                    Path(path_str).unlink(missing_ok=True)
                    logger.debug(f"Removed file: {path_str}")
            except Exception as e:
                logger.error(f"Failed to rollback {path_str}: {str(e)}")
