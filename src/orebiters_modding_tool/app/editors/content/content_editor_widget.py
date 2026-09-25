from typing import Any, ClassVar

from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget
from orebiters_modding_tool.domain.content import Content, ContentType


class ContentEditorWidget[T: Content[Any]](BaseEditorWidget[T]):
    """Base editor widget for content entities."""

    CONTENT_TYPE: ClassVar[ContentType | None] = None

    _registry: ClassVar[dict[ContentType, type[ContentEditorWidget[Any]]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Register concrete editor subclasses."""
        super().__init_subclass__(**kwargs)
        cls._register()

    # =========================================================================
    # Public API
    # =========================================================================

    @classmethod
    def get_class(cls, content_type: ContentType) -> type[ContentEditorWidget[Any]]:
        """Get the editor class for a content type.

        :param content_type: Type of content to edit.
        :returns: Registered editor class.
        :raises KeyError: If no editor is registered for the content type.
        """
        return cls._registry[content_type]

    @classmethod
    def _register(cls) -> None:
        """Register the editor class."""
        content_type = cls.__dict__.get("CONTENT_TYPE")

        if content_type is None:
            return

        if content_type in ContentEditorWidget._registry:
            raise ValueError(f"Editor for content type '{content_type}' is already registered.")

        ContentEditorWidget._registry[content_type] = cls
