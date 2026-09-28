from enum import Enum
from typing import Any


class DisplayEnum(Enum):
    """Enum with display information."""

    def __new__(cls, value: str, display_name: str, singular_display_name: str) -> Any:
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, _value: str, display_name: str, singular_display_name: str) -> None:
        self.display_name = display_name
        self.singular_display_name = singular_display_name
