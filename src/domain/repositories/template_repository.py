from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any
from src.domain.entities.project import Project


class TemplateRepository(ABC):
    @abstractmethod
    def get_template_files(self, template_type: str) -> Dict[str, str]:
        """Get template files for a given template type"""
        pass

    @abstractmethod
    def get_template_content(self, template_path: str) -> str:
        """Get the content of a specific template file"""
        pass
