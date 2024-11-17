from pathlib import Path
from typing import Dict, Any

from src.domain.entities.project import Project
from src.domain.repositories.template_repository import TemplateRepository
from src.domain.commands.base import ProjectCommand


class CoreFilesCommand(ProjectCommand):
    """Handles generation of core project files"""

    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository

    @property
    def template_files(self) -> Dict[str, str]:
        return {
            "main.py": "minimal/main.py.jinja",
            "requirements.txt": "minimal/requirements.txt.jinja",
            ".gitignore": "minimal/gitignore.jinja",
        }

    def execute(
        self, project: Project, context: Dict[str, Any], output_path: Path
    ) -> None:
        for dest_path, template_path in self.template_files.items():
            template = self.template_repository.get_template_content(template_path)
            content = template.render(**context)
            output_path.joinpath(dest_path).write_text(content)
