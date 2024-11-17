from pathlib import Path
from typing import Dict, Any
from loguru import logger
from src.domain.commands.base import ProjectCommand
from src.domain.entities.command_result import CommandResult

from src.domain.entities.project import Project
from src.domain.repositories.template_repository import TemplateRepository
from src.infrastructure.enumerators.command_priority import CommandPriority


class DockerCommand(ProjectCommand):
    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository

    @property
    def name(self) -> str:
        return "docker"

    @property
    def priority(self) -> CommandPriority:
        return CommandPriority.MEDIUM

    @property
    def template_files(self) -> Dict[str, str]:
        return {
            "docker/Dockerfile": "docker/Dockerfile.jinja",
            "docker/docker-compose.yml": "docker/docker-compose.yml.jinja",
        }

    async def validate(self, project: Project, context: Dict[str, Any]) -> bool:
        if not (project.include_dockerfile or project.include_docker_compose):
            return True

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
        if not (project.include_dockerfile or project.include_docker_compose):
            return CommandResult(success=True, changes={})

        logger.info(f"Executing {self.name} command")
        changes = {}
        try:
            docker_path = output_path / "docker"
            docker_path.mkdir(exist_ok=True)
            changes["docker_dir"] = str(docker_path)

            if project.include_dockerfile:
                template = self.template_repository.get_template_content(
                    "docker/Dockerfile.jinja"
                )
                content = template.render(**context)
                file_path = docker_path / "Dockerfile"
                file_path.write_text(content)
                changes[str(file_path)] = None
                logger.debug(f"Created file: {file_path}")

            if project.include_docker_compose:
                template = self.template_repository.get_template_content(
                    "docker/docker-compose.yml.jinja"
                )
                content = template.render(**context)
                file_path = docker_path / "docker-compose.yml"
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
        for path in changes.keys():
            try:
                if path == "docker_dir":
                    Path(path).rmdir()
                    logger.debug(f"Removed directory: {path}")
                else:
                    Path(path).unlink(missing_ok=True)
                    logger.debug(f"Removed file: {path}")
            except Exception as e:
                logger.error(f"Failed to rollback {path}: {str(e)}")
