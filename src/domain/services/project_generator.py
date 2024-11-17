from abc import ABC, abstractmethod
from pathlib import Path
from src.domain.entities.project import Project


class ProjectGenerator(ABC):
    @abstractmethod
    async def generate(self, project: Project, output_path: Path) -> bytes:
        """Generate project structure and return as zip file content"""
        pass
