from PySide6.QtCore import QAbstractItemModel, Qt
from PySide6.QtGui import QResizeEvent, QShowEvent
from PySide6.QtWidgets import QHeaderView, QTableView, QWidget

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
        self._minimum_column_widths: list[int] = []
        self._column_widths_initialized = False
        self._updating_column_widths = False

        self._setup_view()

    def showEvent(self, event: QShowEvent) -> None:
        """Initialize column widths after the view is shown."""
        super().showEvent(event)
        self._initialize_column_widths()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Redistribute column widths when the view is resized."""
        super().resizeEvent(event)

        if self._column_widths_initialized:
            self._update_column_widths()

    def _setup_view(self) -> None:
        """Configure the table view."""
        self.setAlternatingRowColors(True)

        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)

        self.setItemDelegate(ContentTableDelegate(self))

        header = self.horizontalHeader()

        header.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        self.setSortingEnabled(True)

        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.sectionClicked.connect(self._on_header_clicked)

    def _initialize_column_widths(self) -> None:
        """Measure minimum column widths and initialize automatic resizing."""
        if self._column_widths_initialized:
            return

        header = self.horizontalHeader()
        column_count = header.count()

        if column_count == 0:
            return

        self.resizeColumnsToContents()

        self._minimum_column_widths = [header.sectionSize(column) for column in range(column_count)]

        for column in range(column_count):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Interactive)

        self._column_widths_initialized = True
        self._update_column_widths()

    def _update_column_widths(self) -> None:
        """Distribute available space while preserving minimum column widths."""
        if self._updating_column_widths:
            return

        column_count = len(self._minimum_column_widths)

        if column_count == 0:
            return

        available_width = self.viewport().width()
        minimum_width = sum(self._minimum_column_widths)
        extra_width = max(0, available_width - minimum_width)

        extra_per_column, remainder = divmod(extra_width, column_count)

        self._updating_column_widths = True

        try:
            for column, minimum_width in enumerate(self._minimum_column_widths):
                width = minimum_width + extra_per_column

                if column < remainder:
                    width += 1

                self.setColumnWidth(column, width)
        finally:
            self._updating_column_widths = False

    def _on_header_clicked(self, column: int) -> None:
        """Handle a table header click.

        :param column: Clicked column index.
        """
        proxy_model = self.model()

        if not isinstance(proxy_model, TableSortFilterProxyModel):
            return

        if not proxy_model.is_column_sortable(column):
            self.horizontalHeader().setSortIndicator(*self._sort_indicator)
            proxy_model.sort(*self._sort_indicator)
            return

        self._sort_indicator = column, self.horizontalHeader().sortIndicatorOrder()
