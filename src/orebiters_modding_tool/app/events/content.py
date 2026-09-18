from dataclasses import dataclass
from enum import Enum, auto

from orebiters_modding_tool.domain.content import ContentType


class ContentChangeType(Enum):
    """Types of content changes."""

    CREATED = auto()
    UPDATED = auto()
    REMOVED = auto()


@dataclass(frozen=True, slots=True, kw_only=True)
class ContentChange:
    """Describe a content change."""

    change_type: ContentChangeType
    content_type: ContentType
    count: int = 1
    content_name: str | None = None
