from abc import ABC, abstractmethod
from typing import Dict

from jinja2 import Template


class TemplateRepository(ABC):
    @abstractmethod
    def get_template_files(self, template_type: str) -> Dict[str, str]:
        """Get template files for a given template type"""
        pass

    @abstractmethod
    def get_template_content(self, template_path: str) -> Template:
        """Get the content of a specific template file"""
        pass
