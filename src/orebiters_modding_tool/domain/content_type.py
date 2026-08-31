from enum import Enum


class ContentType(Enum):
    """Types of content available in a mod project."""

    CREATURES = "creatures"
    ITEMS = "items"
    RESOURCES = "resources"
