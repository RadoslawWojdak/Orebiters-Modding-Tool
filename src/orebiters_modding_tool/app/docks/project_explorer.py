from PySide6.QtCore import QModelIndex, Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDockWidget, QTreeView, QWidget

from orebiters_modding_tool.domain.content import ContentReference, ContentType


class ProjectExplorer(QDockWidget):
    """Project Explorer widget."""

    TITLE = "Project Explorer"
    CONTENT_TYPE_ROLE = Qt.ItemDataRole.UserRole

    content_open_requested = Signal(ContentReference)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle(self.TITLE)

        self._setup_model()
        self._setup_tree_view()

    def _setup_model(self) -> None:
        """Set up the Project Explorer model."""
        self._model = QStandardItemModel(self)

        items_item = self._create_item(
            "Items",
            content_reference=ContentReference(
                content_type=ContentType.ITEMS,
            ),
        )

        materials_item = self._create_item(
            "Materials",
            content_reference=ContentReference(
                content_type=ContentType.MATERIALS,
            ),
        )

        resources_item = self._create_item(
            "Resources",
            content_reference=ContentReference(
                content_type=ContentType.RESOURCES,
            ),
        )

        self._model.appendRow(items_item)
        self._model.appendRow(materials_item)
        self._model.appendRow(resources_item)

    def _setup_tree_view(self) -> None:
        """Set up the Project Explorer tree view."""
        self._tree_view = QTreeView(self)
        self._tree_view.setModel(self._model)

        self._tree_view.doubleClicked.connect(self._handle_item_double_clicked)

        self.setWidget(self._tree_view)

    def _create_item(
        self,
        text: str,
        *,
        content_reference: ContentReference | None = None,
    ) -> QStandardItem:
        """Create a Project Explorer item.

        :param text: Text displayed for the item.
        :param content_reference: Optional content reference for the item.
        :returns: Configured Project Explorer item.
        """
        item = QStandardItem(text)
        item.setEditable(False)

        if content_reference is not None:
            item.setData(content_reference, self.CONTENT_TYPE_ROLE)

        return item

    def _handle_item_double_clicked(self, index: QModelIndex) -> None:
        """Handle the Project Explorer item double click.

        :param index: Index of the double-clicked item.
        """
        item = self._model.itemFromIndex(index)

        if item is None:
            return

        content_reference = item.data(self.CONTENT_TYPE_ROLE)

        if not isinstance(content_reference, ContentReference):
            return

        self.content_open_requested.emit(content_reference)
