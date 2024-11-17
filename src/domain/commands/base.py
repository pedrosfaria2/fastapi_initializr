from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

from src.domain.entities.command_result import CommandResult
from src.domain.entities.project import Project
from src.infrastructure.enumerators.command_priority import CommandPriority


class ProjectCommand(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the command"""
        pass

    @property
    def priority(self) -> CommandPriority:
        """Command execution priority. Can be overridden by concrete commands"""
        return CommandPriority.MEDIUM

    @property
    @abstractmethod
    def template_files(self) -> Dict[str, str]:
        """Define template files required by this command"""
        pass

    @abstractmethod
    async def execute(
        self, project: Project, context: Dict[str, Any], output_path: Path
    ) -> CommandResult:
        """Execute the command"""
        pass

    @abstractmethod
    async def validate(self, project: Project, context: Dict[str, Any]) -> bool:
        """Validate command can be executed with given project and context"""
        pass

    @abstractmethod
    async def rollback(
        self, project: Project, context: Dict[str, Any], changes: Dict[str, Any]
    ) -> None:
        """Rollback changes made by this command"""
        pass
