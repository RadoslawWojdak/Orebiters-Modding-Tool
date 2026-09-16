from PySide6.QtCore import QAbstractItemModel, Qt
from PySide6.QtWidgets import QTableView, QWidget

from orebiters_modding_tool.app.delegates.content_table_delegate import ContentTableDelegate
from orebiters_modding_tool.app.models.table_sort_filter_proxy_model import (
    TableSortFilterProxyModel,
)


class ContentTableView(QTableView):
    """Table view for project content."""

    def __init__(self, model: QAbstractItemModel, parent: QWidget | None = None) -> None:
        """Initialize the content table view.

        :param model: Model displayed by the table.
        :param parent: Optional parent widget.
        """
        super().__init__(parent)

        self.setModel(model)

        self._sort_indicator = (-1, Qt.SortOrder.AscendingOrder)

        self._setup_view()

    def _setup_view(self) -> None:
        """Configure the table view."""
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)

        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)

        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)

        self.setItemDelegate(ContentTableDelegate(self))

        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.sectionClicked.connect(self._on_header_clicked)

    def _on_header_clicked(self, column: int) -> None:
        """Handle a table header click.

        :param column: Clicked column index.
        """
        proxy_model = self.model()

        if not isinstance(proxy_model, TableSortFilterProxyModel):
            return

        if not proxy_model.is_column_sortable(column):
            self.horizontalHeader().setSortIndicator(*self._sort_indicator)
            return

        if not self.isSortingEnabled():
            self.setSortingEnabled(True)
            self.sortByColumn(column, Qt.SortOrder.AscendingOrder)

        self._sort_indicator = column, self.horizontalHeader().sortIndicatorOrder()
