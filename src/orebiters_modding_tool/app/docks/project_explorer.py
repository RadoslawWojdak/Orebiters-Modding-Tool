from PySide6.QtCore import QModelIndex, Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QDockWidget, QTreeView, QWidget

from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.services.project_service import ProjectService


class ProjectExplorer(QDockWidget):
    """Project Explorer widget."""

    TITLE = "Project Explorer"
    CONTENT_TYPE_ROLE = Qt.ItemDataRole.UserRole

    content_open_requested = Signal(ContentReference)

    def __init__(self, project_service: ProjectService, parent: QWidget | None = None) -> None:
        """Initialize the Project Explorer.

        :param project_service: Service used to retrieve project content.
        :param parent: Optional parent widget.
        """
        super().__init__(parent)

        self._project_service = project_service

        self.setWindowTitle(self.TITLE)

        self._setup_model()
        self._setup_tree_view()
        self.refresh()

    def refresh(self) -> None:
        """Refresh the Project Explorer contents."""
        expanded_categories = self._get_expanded_categories()

        self._model.clear()

        for content_type in ContentType:
            self._create_category(content_type.display_name, content_type)

        self._restore_expanded_categories(expanded_categories)

    def _setup_model(self) -> None:
        """Set up the Project Explorer model."""
        self._model = QStandardItemModel(self)

    def _setup_tree_view(self) -> None:
        """Set up the Project Explorer tree view."""
        self._tree_view = QTreeView(self)
        self._tree_view.setModel(self._model)
        self._tree_view.setHeaderHidden(True)
        self._tree_view.setExpandsOnDoubleClick(False)

        self._tree_view.doubleClicked.connect(self._handle_item_double_clicked)

        self.setWidget(self._tree_view)

    def _create_category(self, text: str, content_type: ContentType) -> None:
        """Create a content category and its children.

        :param text: Text displayed for the category.
        :param content_type: Type of content represented by the category.
        """
        category_item = self._create_item(
            text,
            content_reference=ContentReference(
                content_type=content_type,
            ),
        )

        content_references = self._get_active_project_references(content_type)

        for content_reference in sorted(content_references, key=self._content_reference_sort_key):
            content_item = self._create_item(
                content_reference.content_id,
                content_reference=content_reference,
            )
            category_item.appendRow(content_item)

        self._model.appendRow(category_item)

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

    def _get_expanded_categories(self) -> set[ContentType]:
        """Return content categories that are currently expanded.

        :returns: Types of expanded content categories.
        """
        expanded_categories: set[ContentType] = set()

        for row in range(self._model.rowCount()):
            item = self._model.item(row)
            assert item is not None

            content_reference = item.data(self.CONTENT_TYPE_ROLE)

            if not isinstance(content_reference, ContentReference):
                continue

            if not content_reference.is_category:
                continue

            if self._tree_view.isExpanded(item.index()):
                expanded_categories.add(content_reference.content_type)

        return expanded_categories

    def _restore_expanded_categories(self, content_types: set[ContentType]) -> None:
        """Restore the expanded state of content categories.

        :param content_types: Types of categories that should be expanded.
        """
        for row in range(self._model.rowCount()):
            item = self._model.item(row)
            assert item is not None

            content_reference = item.data(self.CONTENT_TYPE_ROLE)

            if not isinstance(content_reference, ContentReference):
                continue

            if content_reference.content_type in content_types:
                self._tree_view.expand(item.index())

    def _get_active_project_references(self, content_type: ContentType) -> list[ContentReference]:
        """Get content references belonging to the active project.

        :param content_type: Type of content to retrieve.
        :returns: References belonging to the active project.
        """
        active_project = self._project_service.active_project

        if active_project is None:
            return []

        project_prefix = f"{active_project.qualified_id}."

        return [
            reference
            for reference in self._project_service.get_content_references(content_type)
            if reference.qualified_id is not None
            and reference.qualified_id.startswith(project_prefix)
        ]

    @staticmethod
    def _content_reference_sort_key(content_reference: ContentReference) -> str:
        """Return the value used to sort a content reference.

        :param content_reference: Content reference to sort.
        :returns: Case-insensitive content ID.
        """
        return content_reference.content_id.casefold()

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
