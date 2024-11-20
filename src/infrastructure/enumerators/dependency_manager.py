from enum import Enum


class DependencyManager(str, Enum):
    PIP = "pip"
    POETRY = "poetry"
