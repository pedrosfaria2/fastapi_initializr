from pathlib import Path
from typing import Dict
from jinja2 import Environment, FileSystemLoader
from src.domain.repositories.template_repository import TemplateRepository
from src.domain.entities.project import TemplateType


class JinjaTemplateRepository(TemplateRepository):
    def __init__(self, template_dir: str = "src/infrastructure/templates"):
        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def get_template_files(self, template_type: str) -> Dict[str, str]:
        template_dir = template_type.lower()

        template_mapping = {
            TemplateType.MINIMAL.value: {
                "main.py": f"{template_dir}/main.py.jinja",
                "requirements.txt": f"{template_dir}/requirements.txt.jinja",
                "README.md": f"{template_dir}/README.md.jinja",
                ".gitignore": f"{template_dir}/gitignore.jinja",
            }
        }
        return template_mapping.get(template_type.lower(), {})

    def get_template_content(self, template_path: str) -> str:
        return self.env.get_template(template_path)
