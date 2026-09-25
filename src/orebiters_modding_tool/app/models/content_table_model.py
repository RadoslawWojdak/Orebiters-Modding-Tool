from typing import Any, ClassVar

from PySide6.QtCore import Qt

from orebiters_modding_tool.app.models.base_table_model import BaseTableModel, ModelIndex
from orebiters_modding_tool.domain.content import Content, ContentType


class ContentTableModel[T: Content[Any]](BaseTableModel[T]):
    """Base table model for content."""

    CONTENT_TYPE: ClassVar[ContentType]

    _registry: ClassVar[dict[ContentType, type[ContentTableModel[Any]]]] = {}

    CONTENT_STATE_ROLE = Qt.ItemDataRole.UserRole + 1

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Register concrete content table models."""
        super().__init_subclass__(**kwargs)
        cls._register()

    @classmethod
    def get_class(cls, content_type: ContentType) -> type[ContentTableModel[Any]]:
        """Return the table model class registered for the given content type.

        :param content_type: Type of content to retrieve.
        :returns: Registered table model class.
        :raises KeyError: If no model is registered for the given type.
        """
        return cls._registry[content_type]

    def data(self, index: ModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        """Return data for a table cell.

        :param index: Cell model index.
        :param role: Requested data role.
        :returns: Data for the requested role.
        """
        if role == self.CONTENT_STATE_ROLE:
            if not index.isValid():
                return None

            return self.get_item(index.row()).state

        return super().data(index, role)

    def refresh_content_states(self) -> None:
        """Refresh the displayed content states."""
        if not self._items:
            return

        self.dataChanged.emit(
            self.index(0, 0),
            self.index(self.rowCount() - 1, self.columnCount() - 1),
            [self.CONTENT_STATE_ROLE],
        )

    @classmethod
    def _register(cls) -> None:
        """Register the content table model."""
        content_type = cls.__dict__.get("CONTENT_TYPE")

        if content_type is None:
            return

        if content_type in ContentTableModel._registry:
            raise ValueError(f"Content table model for '{content_type}' is already registered.")

        ContentTableModel._registry[content_type] = cls
