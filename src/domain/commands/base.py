from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any
from src.domain.entities.project import Project


class ProjectCommand(ABC):
    """Base interface for project generation commands"""

    @abstractmethod
    def execute(
        self, project: Project, context: Dict[str, Any], output_path: Path
    ) -> None:
        """Execute the command"""
        pass

    @property
    @abstractmethod
    def template_files(self) -> Dict[str, str]:
        """Get template files mapping for this command"""
        pass
