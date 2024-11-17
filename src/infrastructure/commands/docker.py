from pathlib import Path
from typing import Dict, Any

from src.domain.entities.project import Project
from src.domain.repositories.template_repository import TemplateRepository
from src.domain.commands.base import ProjectCommand


class DockerCommand(ProjectCommand):
    """Handles Docker-related file generation"""

    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository

    @property
    def template_files(self) -> Dict[str, str]:
        return {
            "docker/Dockerfile": "docker/Dockerfile.jinja",
            "docker/docker-compose.yml": "docker/docker-compose.yml.jinja",
        }

    def execute(
        self, project: Project, context: Dict[str, Any], output_path: Path
    ) -> None:
        if not (project.include_dockerfile or project.include_docker_compose):
            return

        docker_path = output_path / "docker"
        docker_path.mkdir(exist_ok=True)

        if project.include_dockerfile:
            template = self.template_repository.get_template_content(
                "docker/Dockerfile.jinja"
            )
            content = template.render(**context)
            docker_path.joinpath("Dockerfile").write_text(content)

        if project.include_docker_compose:
            template = self.template_repository.get_template_content(
                "docker/docker-compose.yml.jinja"
            )
            content = template.render(**context)
            docker_path.joinpath("docker-compose.yml").write_text(content)
