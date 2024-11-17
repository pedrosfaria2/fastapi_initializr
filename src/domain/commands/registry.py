from typing import Dict, List
from loguru import logger
from src.domain.commands.base import ProjectCommand


class CommandRegistry:
    """Registry for available project commands"""

    def __init__(self):
        self._commands: Dict[str, ProjectCommand] = {}

    def register(self, command: ProjectCommand) -> None:
        """
        Register a command instance

        Args:
            command: The command instance to register
        """
        logger.info(f"Registering command: {command.name}")
        self._commands[command.name] = command

    def get_command(self, name: str) -> ProjectCommand:
        """Get command instance by name"""
        if name not in self._commands:
            raise ValueError(f"Command {name} not found")
        return self._commands[name]

    def get_all_commands(self) -> List[ProjectCommand]:
        """Get all registered command instances sorted by priority"""
        return sorted(self._commands.values(), key=lambda x: x.priority)
