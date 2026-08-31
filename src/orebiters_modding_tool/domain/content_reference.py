from dataclasses import dataclass

from orebiters_modding_tool.domain.content_type import ContentType


@dataclass(frozen=True, slots=True, kw_only=True)
class ContentReference:
    """Reference to content displayed in the application."""

    content_type: ContentType
    content_id: int | None = None
