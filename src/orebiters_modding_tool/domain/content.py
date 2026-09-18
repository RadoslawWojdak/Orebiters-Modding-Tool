from dataclasses import dataclass
from enum import Enum, auto
from typing import ClassVar


class ContentType(Enum):
    """Types of content available in a mod project."""

    _value_: str

    ITEMS = ("items", "Items", "Item")
    MATERIALS = ("materials", "Materials", "Material")
    RESOURCES = ("resources", "Resources", "Resource")

    def __init__(self, value: str, display_name: str, singular_display_name: str) -> None:
        self._value_ = value
        self.display_name = display_name
        self.singular_display_name = singular_display_name


class ContentState(Enum):
    """State of content within the editor."""

    SAVED = auto()
    NEW = auto()
    MODIFIED = auto()


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
    def namespace(self) -> str:
        """Get the namespace of the owning mod.

        :returns: Namespace of the owning mod.
        :raises ValueError: If the reference does not target specific content.
        """
        if self.qualified_id is None:
            raise ValueError("Content reference does not target specific content.")

        return self.qualified_id.split(".")[0]

    @property
    def mod_id(self) -> str:
        """Get the ID of the owning mod.

        :returns: ID of the owning mod.
        :raises ValueError: If the reference does not target specific content.
        """
        if self.qualified_id is None:
            raise ValueError("Content reference does not target specific content.")

        return self.qualified_id.split(".")[1]

    @property
    def content_id(self) -> str:
        """Get the local content ID.

        :returns: Local content ID.
        :raises ValueError: If the reference does not target specific content.
        """
        if self.qualified_id is None:
            raise ValueError("Content reference does not target specific content.")

        return self.qualified_id.split(".")[2]


@dataclass(slots=True, kw_only=True)
class Content[TLocalization: ContentLocalization]:
    """Editable content definition."""

    CONTENT_TYPE: ClassVar[ContentType]

    id: str
    localizations: dict[str, TLocalization]

    state: ContentState = ContentState.SAVED

    def get_qualified_id(self, mod_qualified_id: str) -> str:
        """Build a fully qualified content ID.

        :param mod_qualified_id: ID of the content owner.
        :returns: Fully qualified content ID.
        """
        return f"{mod_qualified_id}.{self.id}"
