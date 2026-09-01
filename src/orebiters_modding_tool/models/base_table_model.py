from PySide6.QtCore import QAbstractTableModel, QModelIndex, QObject, QPersistentModelIndex, Qt

from orebiters_modding_tool.models.column import Column

ModelIndex = QModelIndex | QPersistentModelIndex
EMPTY_MODEL_INDEX = QModelIndex()


class BaseTableModel[T](QAbstractTableModel):
    """Base table model for editable content."""

    COLUMNS: tuple[Column[T], ...] = ()

    def __init__(self, items: list[T], parent: QObject | None = None) -> None:
        """Initialize the table model.

        :param items: Items displayed by the model.
        :param parent: Parent Qt object.
        """
        super().__init__(parent)

        self._items = items

    def rowCount(self, parent: ModelIndex = EMPTY_MODEL_INDEX) -> int:
        """Return the number of rows.

        :param parent: Parent model index.
        :returns: Number of rows.
        """
        if parent.isValid():
            return 0

        return len(self._items)

    def columnCount(self, parent: ModelIndex = EMPTY_MODEL_INDEX) -> int:
        """Return the number of columns.

        :param parent: Parent model index.
        :returns: Number of columns.
        """
        if parent.isValid():
            return 0

        return len(self.COLUMNS)

    def data(self, index: ModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        """Return data for a table cell.

        :param index: Cell model index.
        :param role: Requested data role.
        :returns: Data for the requested role.
        """
        if not index.isValid():
            return None

        item = self._items[index.row()]
        column = self.COLUMNS[index.column()]

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return column.getter(item)

        if role == Qt.ItemDataRole.ToolTipRole:
            return column.tooltip

        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object | None:
        """Return header data.

        :param section: Header section index.
        :param orientation: Header orientation.
        :param role: Requested data role.
        :returns: Header data.
        """
        if orientation != Qt.Orientation.Horizontal:
            return None

        if not 0 <= section < len(self.COLUMNS):
            return None

        column = self.COLUMNS[section]

        if role == Qt.ItemDataRole.DisplayRole:
            return column.header

        if role == Qt.ItemDataRole.ToolTipRole:
            return column.tooltip

        return None

    def flags(self, index: ModelIndex) -> Qt.ItemFlag:
        """Return interaction flags for a table cell.

        :param index: Cell model index.
        :returns: Available interactions.
        """
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        column = self.COLUMNS[index.column()]

        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

        if column.setter is not None:
            flags |= Qt.ItemFlag.ItemIsEditable

        return flags

    def setData(
        self,
        index: ModelIndex,
        value: object,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        """Update data in a table cell.

        :param index: Cell model index.
        :param value: New value.
        :param role: Data role being updated.
        :returns: True if the data was updated.
        """
        if not index.isValid():
            return False

        if role != Qt.ItemDataRole.EditRole:
            return False

        item = self._items[index.row()]
        column = self.COLUMNS[index.column()]

        if column.setter is None:
            return False

        column.setter(item, value)

        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])

        return True
