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

    # =========================================================================
    # Private API
    # =========================================================================

    def _get_qualified_id(self) -> str:
        """Return the qualified ID of the edited content.

        :returns: Qualified ID of the edited content.
        :raises KeyError: If the mod ID is missing from the context.
        :raises TypeError: If the mod ID is not a string.
        """
        mod_id = self._context["mod_id"]

        if not isinstance(mod_id, str):
            raise TypeError("Context value 'mod_id' must be a string.")

        return self._item.get_qualified_id(mod_id)

    @classmethod
    def _register(cls) -> None:
        """Register the editor class."""
        content_type = cls.__dict__.get("CONTENT_TYPE")

        if content_type is None:
            return

        if content_type in ContentEditorWidget._registry:
            raise ValueError(f"Editor for content type '{content_type}' is already registered.")

        ContentEditorWidget._registry[content_type] = cls
