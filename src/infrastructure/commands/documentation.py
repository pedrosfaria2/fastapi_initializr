from pathlib import Path
from typing import Dict, Any

from src.domain.entities.project import Project
from src.domain.repositories.template_repository import TemplateRepository
from src.domain.commands.base import ProjectCommand


class DocumentationCommand(ProjectCommand):
    """Handles documentation file generation"""

    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository

    @property
    def template_files(self) -> Dict[str, str]:
        return {"README.md": "readme/README.md.jinja"}

    def execute(
        self, project: Project, context: Dict[str, Any], output_path: Path
    ) -> None:
        template = self.template_repository.get_template_content(
            "readme/README.md.jinja"
        )
        content = template.render(**context)
        output_path.joinpath("README.md").write_text(content)
