from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class ContentType(Enum):
    """Types of content available in a mod project."""

    ITEMS = "items"
    MATERIALS = "materials"
    RESOURCES = "resources"


@dataclass(slots=True, kw_only=True)
class ContentLocalization:
    """Localized base content text."""

    one: str = ""
    few: str = ""
    many: str = ""


@dataclass(frozen=True, slots=True, kw_only=True)
class ContentReference:
    """Reference to uniquely identifiable content."""

    content_type: ContentType
    qualified_id: str | None = None

    @property
    def is_category(self) -> bool:
        """Check whether the reference targets a content category.

        :returns: True if the reference targets a category.
        """
        return self.qualified_id is None

    @property
    def mod_id(self) -> str:
        """Get the ID of the owning mod.

        :returns: ID of the owning mod.
        :raises ValueError: If the reference does not target specific content.
        """
        if self.qualified_id is None:
            raise ValueError("Content reference does not target specific content.")

        return self.qualified_id.split(".", maxsplit=1)[0]

    @property
    def content_id(self) -> str:
        """Get the local content ID.

        :returns: Local content ID.
        :raises ValueError: If the reference does not target specific content.
        """
        if self.qualified_id is None:
            raise ValueError("Content reference does not target specific content.")

        return self.qualified_id.split(".", maxsplit=1)[1]


@dataclass(slots=True, kw_only=True)
class Content[TLocalization: ContentLocalization]:
    """Editable content definition."""

    CONTENT_TYPE: ClassVar[ContentType]

    id: str
    localizations: dict[str, TLocalization]

    def get_qualified_id(self, mod_qualified_id: str) -> str:
        """Build a fully qualified content ID.

        :param mod_qualified_id: ID of the content owner.
        :returns: Fully qualified content ID.
        """
        return f"{mod_qualified_id}.{self.id}"
