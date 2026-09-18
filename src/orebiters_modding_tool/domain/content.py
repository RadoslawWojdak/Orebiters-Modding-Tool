from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, ClassVar, get_args, get_origin


class ContentType(Enum):
    """Types of content available in a mod project."""

    _value_: str

    # ITEMS = ("items", "Items", "Item")
    MATERIALS = ("materials", "Materials", "Material")
    # RESOURCES = ("resources", "Resources", "Resource")

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


@dataclass(kw_only=True)
class Content[TLocalization: ContentLocalization]:
    """Editable content definition."""

    CONTENT_TYPE: ClassVar[ContentType]
    LOCALIZATION_CLASS: ClassVar[type[ContentLocalization]]

    _registry: ClassVar[dict[ContentType, type[Content[Any]]]] = {}

    id: str
    localizations: dict[str, TLocalization]

    state: ContentState = ContentState.SAVED

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize concrete content subclasses."""
        super().__init_subclass__(**kwargs)

        cls._resolve_localization_class()
        cls._register()

    @classmethod
    def get_class(cls, content_type: ContentType) -> type[Content[Any]]:
        """Return the content class registered for the given type.

        :param content_type: Type of content to retrieve.
        :returns: Registered content class.
        :raises KeyError: If no class is registered for the given type.
        """
        return cls._registry[content_type]

    def get_qualified_id(self, mod_qualified_id: str) -> str:
        """Build a fully qualified content ID.

        :param mod_qualified_id: ID of the content owner.
        :returns: Fully qualified content ID.
        """
        return f"{mod_qualified_id}.{self.id}"

    @classmethod
    def _resolve_localization_class(cls) -> None:
        """Resolve the localization class from generic bases."""
        for base in getattr(cls, "__orig_bases__", ()):
            if get_origin(base) is not Content:
                continue

            localization_class = get_args(base)[0]

            if not isinstance(localization_class, type):
                raise TypeError(f"Could not resolve localization class for '{cls.__name__}'.")

            if not issubclass(localization_class, ContentLocalization):
                raise TypeError(
                    f"'{localization_class.__name__}' must inherit from ContentLocalization."
                )

            cls.LOCALIZATION_CLASS = localization_class
            return

        for base in cls.__bases__:
            localization_class = getattr(base, "LOCALIZATION_CLASS", None)

            if localization_class is not None:
                cls.LOCALIZATION_CLASS = localization_class
                return

    @classmethod
    def _register(cls) -> None:
        """Register the content class."""
        content_type = cls.__dict__.get("CONTENT_TYPE")

        if content_type is None:
            return

        if content_type in Content._registry:
            raise ValueError(f"Content type '{content_type}' is already registered.")

        Content._registry[content_type] = cls
