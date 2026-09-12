from PySide6.QtCore import QModelIndex, QObject, QPersistentModelIndex, QSortFilterProxyModel, Qt

from orebiters_modding_tool.app.models.base_table_model import BaseTableModel


class TableSortFilterProxyModel[T](QSortFilterProxyModel):
    """Proxy model providing generic sorting and text filtering for table models."""

    def __init__(
        self,
        source_model: BaseTableModel[T] | None = None,
        parent: QObject | None = None,
    ) -> None:
        """Initialize the proxy model.

        :param source_model: Model providing the source data.
        :param parent: Parent Qt object.
        """
        super().__init__(parent)

        self._filter_text = ""

        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        if source_model is not None:
            self.setSourceModel(source_model)

    def set_filter_text(self, text: str) -> None:
        """Set the text used to filter rows.

        :param text: Text that must occur in a filterable column.
        """
        normalized_text = text.strip()

        if normalized_text == self._filter_text:
            return

        self._filter_text = normalized_text
        self.setFilterFixedString(normalized_text)

    def filter_text(self) -> str:
        """Return the current filter text.

        :returns: Current filter text.
        """
        return self._filter_text

    def filterAcceptsRow(
        self,
        source_row: int,
        source_parent: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Return whether a source row passes the current filter.

        :param source_row: Source row being tested.
        :param source_parent: Parent source index.
        :returns: True if the row should be visible.
        """
        if not self._filter_text:
            return True

        source_model = self._get_source_model()

        for column_index, column in enumerate(source_model.COLUMNS):
            if not column.filterable:
                continue

            index = source_model.index(source_row, column_index, source_parent)
            value = source_model.data(index, Qt.ItemDataRole.DisplayRole)

            if value is not None and self.filterRegularExpression().match(str(value)).hasMatch():
                return True

        return False

    def lessThan(
        self,
        left: QModelIndex | QPersistentModelIndex,
        right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Return whether the left value should precede the right value.

        :param left: Left source index.
        :param right: Right source index.
        :returns: True if the left value precedes the right value.
        """
        source_model = self._get_source_model()
        column = source_model.COLUMNS[left.column()]

        if not column.sortable:
            return False

        left_value = source_model.data(left, Qt.ItemDataRole.DisplayRole)
        right_value = source_model.data(right, Qt.ItemDataRole.DisplayRole)

        if left_value is None:
            return right_value is not None

        if right_value is None:
            return False

        if isinstance(left_value, int | float) and isinstance(right_value, int | float):
            return left_value < right_value

        return str(left_value).casefold() < str(right_value).casefold()

    def is_column_sortable(self, column: int) -> bool:
        """Return whether a column can be sorted.

        :param column: Column index.
        :returns: True if the column is sortable.
        """
        return self._get_source_model().COLUMNS[column].sortable

    def _get_source_model(self) -> BaseTableModel[T]:
        """Return the source table model.

        :returns: Source table model.
        :raises TypeError: If the source model is not a BaseTableModel.
        """
        source_model = self.sourceModel()

        if not isinstance(source_model, BaseTableModel):
            raise TypeError("Source model must be a BaseTableModel.")

        return source_model
