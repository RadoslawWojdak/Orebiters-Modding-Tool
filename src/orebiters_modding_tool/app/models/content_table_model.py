from typing import Any

from PySide6.QtCore import Qt

from orebiters_modding_tool.app.models.base_table_model import (
    BaseTableModel,
    ModelIndex,
)
from orebiters_modding_tool.domain.content import Content


class ContentTableModel[T: Content[Any]](BaseTableModel[T]):
    """Base table model for content."""

    CONTENT_STATE_ROLE = Qt.ItemDataRole.UserRole

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
