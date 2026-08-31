from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDockWidget, QTreeView, QWidget


class ProjectExplorer(QDockWidget):
    """Project Explorer widget."""

    TITLE = "Project Explorer"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle(self.TITLE)

        self._setup_model()
        self._setup_tree_view()

    def _setup_model(self) -> None:
        """Set up the model for the project explorer."""
        self._model = QStandardItemModel(self)

        entities_item = self._create_item("Entities")
        creatures_item = self._create_item("Creatures")

        items_item = self._create_item("Items")
        resources_item = self._create_item("Resources")

        entities_item.appendRow(creatures_item)

        self._model.appendRow(entities_item)
        self._model.appendRow(items_item)
        self._model.appendRow(resources_item)

    def _setup_tree_view(self) -> None:
        """Set up the tree view for the project explorer."""
        self._tree_view = QTreeView(self)
        self._tree_view.setModel(self._model)
        self.setWidget(self._tree_view)

    def _create_item(self, text: str) -> QStandardItem:
        """Create a project explorer item.

        :param text: Text displayed for the item.
        :returns: Configured project explorer item.
        """
        item = QStandardItem(text)
        item.setEditable(False)

        return item
