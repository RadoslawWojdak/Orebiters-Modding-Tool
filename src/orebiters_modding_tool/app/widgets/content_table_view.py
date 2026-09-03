from PySide6.QtCore import QAbstractItemModel
from PySide6.QtWidgets import QTableView, QWidget


class ContentTableView(QTableView):
    """Table view for project content."""

    def __init__(self, model: QAbstractItemModel, parent: QWidget | None = None) -> None:
        """Initialize the content table view.

        :param model: Model displayed by the table.
        :param parent: Optional parent widget.
        """
        super().__init__(parent)

        self.setModel(model)

        self._setup_view()

    def _setup_view(self) -> None:
        """Configure the table view."""
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)

        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)

        self.setEditTriggers(
            QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.EditKeyPressed,
        )

        horizontal_header = self.horizontalHeader()
        horizontal_header.setStretchLastSection(True)
