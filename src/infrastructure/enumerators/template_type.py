from enum import Enum


class TemplateType(str, Enum):
    MINIMAL = "minimal"
    BASIC = "basic"
    FULL = "full"
