from typing import Optional, Dict, Any


class CommandValidationError(Exception):
    """Exception raised when command validation fails"""

    def __init__(
        self,
        message: str,
        command_name: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        self.command_name = command_name
        self.details = details or {}
        self.original_error = original_error

        error_msg = f"Command '{command_name}' validation failed: {message}"
        if details:
            error_msg += f"\nDetails: {details}"
        if original_error:
            error_msg += f"\nCaused by: {str(original_error)}"

        super().__init__(error_msg)


class CommandExecutionError(Exception):
    """Exception raised when command execution fails"""

    def __init__(
        self,
        message: str,
        command_name: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        self.command_name = command_name
        self.details = details or {}
        self.original_error = original_error

        error_msg = f"Command '{command_name}' execution failed: {message}"
        if details:
            error_msg += f"\nDetails: {details}"
        if original_error:
            error_msg += f"\nCaused by: {str(original_error)}"

        super().__init__(error_msg)


class CommandRollbackError(Exception):
    """Exception raised when command rollback fails"""

    def __init__(
        self,
        message: str,
        command_name: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        self.command_name = command_name
        self.details = details or {}
        self.original_error = original_error

        error_msg = f"Command '{command_name}' rollback failed: {message}"
        if details:
            error_msg += f"\nDetails: {details}"
        if original_error:
            error_msg += f"\nCaused by: {str(original_error)}"

        super().__init__(error_msg)
