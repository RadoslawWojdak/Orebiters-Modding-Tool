from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QAbstractProxyModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QAction, QFont, QIcon, QKeySequence
from PySide6.QtWidgets import QLabel, QLineEdit, QStackedLayout, QToolBar, QVBoxLayout, QWidget

from orebiters_modding_tool.app.models.content_table_model import ContentTableModel
from orebiters_modding_tool.app.models.table_sort_filter_proxy_model import (
    TableSortFilterProxyModel,
)
from orebiters_modding_tool.app.views.content_table_view import ContentTableView
from orebiters_modding_tool.domain.content import Content, ContentReference


@dataclass(frozen=True, slots=True, kw_only=True)
class ContentOverviewConfig:
    """Configuration for a content overview widget."""

    title: str
    empty_message: str


class ContentOverviewWidget[T: Content[Any]](QWidget):
    """Content overview displayed in the workspace."""

    TITLE_FONT_SIZE = 24
    TITLE_CONTENT_SPACING = 24
    MESSAGE_FONT_SIZE = 12

    add_requested = Signal(ContentReference)
    edit_requested = Signal(ContentReference, list)
    delete_requested = Signal(ContentReference, list)

    def __init__(
        self,
        content_reference: ContentReference,
        config: ContentOverviewConfig,
        model: ContentTableModel[T],
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the content overview.

        :param content_reference: Reference represented by this overview.
        :param config: Overview configuration.
        :param model: Model displayed by the content table.
        :param parent: Optional parent widget.
        """
        super().__init__(parent)

        self._content_reference = content_reference
        self._model = model
        self._proxy_model = TableSortFilterProxyModel(model)
        self._proxy_model.setSortRole(ContentTableModel.SORT_ROLE)
        self._config = config

        self._setup_layout()
        self._connect_signals()
        self._update_content_visibility()

    # =========================================================================
    # Public API
    # =========================================================================

    @property
    def content_reference(self) -> ContentReference:
        """Return the reference represented by this widget.

        :returns: Content reference.
        """
        return self._content_reference

    @property
    def model(self) -> ContentTableModel[T]:
        """Return the table model.

        :returns: Table model used by the overview.
        """
        return self._model

    def refresh_content_states(self) -> None:
        """Refresh the displayed content states."""
        self._model.refresh_content_states()

    # =========================================================================
    # Setup
    # =========================================================================

    def _setup_layout(self) -> None:
        """Set up the content overview layout."""
        layout = QVBoxLayout(self)

        layout.addStretch()
        layout.addWidget(self._create_title_label())
        layout.addSpacing(self.TITLE_CONTENT_SPACING)

        self._toolbar = self._create_toolbar()
        layout.addWidget(self._toolbar)

        self._filter_edit = self._create_filter_edit()
        layout.addWidget(self._filter_edit)

        self._content_layout = self._create_content_layout()
        layout.addLayout(self._content_layout)

        layout.addStretch()

    def _create_toolbar(self) -> QToolBar:
        """Create the local content toolbar.

        :returns: Configured content toolbar.
        """
        toolbar = QToolBar(self)
        toolbar.setMovable(False)

        self._add_action = QAction(QIcon(":/icons/add.svg"), "Add", self)
        self._add_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        self._add_action.triggered.connect(self._on_add_requested)

        self._edit_action = QAction(QIcon(":/icons/edit.svg"), "Edit", self)
        self._edit_action.setShortcut(Qt.Key.Key_Return)
        self._edit_action.triggered.connect(self._on_edit_requested)

        self._delete_action = QAction(QIcon(":/icons/delete.svg"), "Delete", self)
        self._delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self._delete_action.triggered.connect(self._on_delete_requested)

        self._select_all_action = QAction("Select All", self)
        self._select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        self._select_all_action.triggered.connect(self._select_all_content)

        toolbar.addAction(self._add_action)
        toolbar.addAction(self._edit_action)
        toolbar.addAction(self._delete_action)

        self.addAction(self._select_all_action)

        return toolbar

    def _create_filter_edit(self) -> QLineEdit:
        """Create the content filter input.

        :returns: Configured filter input.
        """
        filter_edit = QLineEdit(self)
        filter_edit.setObjectName("filter_edit")
        filter_edit.setPlaceholderText(f"Search {self._config.title.lower()}...")
        filter_edit.setClearButtonEnabled(True)

        return filter_edit

    def _create_content_layout(self) -> QStackedLayout:
        """Create the switchable content area.

        :returns: Configured stacked content layout.
        """
        content_layout = QStackedLayout()

        self._message_label = self._create_message_label()
        self._table_view = ContentTableView(self._proxy_model, self)

        content_layout.addWidget(self._message_label)
        content_layout.addWidget(self._table_view)

        return content_layout

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self._model.rowsInserted.connect(self._update_content_visibility)
        self._model.rowsRemoved.connect(self._update_content_visibility)
        self._model.modelReset.connect(self._update_content_visibility)

        self._filter_edit.textChanged.connect(self._on_filter_text_changed)

        self._table_view.doubleClicked.connect(self._on_item_double_clicked)

    def _get_selected_items(self) -> list[T]:
        """Return the selected content items.

        :returns: Selected content items.
        """
        selection_model = self._table_view.selectionModel()
        return [self._get_item_from_view_index(index) for index in selection_model.selectedRows()]

    def _get_item_from_view_index(self, index: QModelIndex) -> T:
        """Return the item represented by a view index.

        :param index: View index of the item.
        :returns: Content item represented by the index.
        """
        model = self._table_view.model()

        while isinstance(model, QAbstractProxyModel):
            index = model.mapToSource(index)
            model = model.sourceModel()

        return self._model.get_item(index.row())

    # =========================================================================
    # Actions
    # =========================================================================

    def _on_add_requested(self) -> None:
        """Request adding a new content item."""
        self.add_requested.emit(self._content_reference)

    def _on_edit_requested(self) -> None:
        """Request editing selected content items."""
        items = self._get_selected_items()

        if not items:
            return

        self.edit_requested.emit(self._content_reference, items)

    def _on_delete_requested(self) -> None:
        """Request deleting selected content items."""
        items = self._get_selected_items()

        if not items:
            return

        self.delete_requested.emit(self._content_reference, items)

    def _on_item_double_clicked(self, index: QModelIndex) -> None:
        """Request editing the double-clicked content item.

        :param index: View index of the double-clicked item.
        """
        item = self._get_item_from_view_index(index)
        self.edit_requested.emit(self._content_reference, [item])

    def _on_filter_text_changed(self, text: str) -> None:
        """Handle a change in the filter text.

        :param text: New filter text.
        """
        self._proxy_model.set_filter_text(text)
        self._update_content_visibility()

    def _select_all_content(self) -> None:
        """Select all rows in the content table."""
        self._table_view.selectAll()

    # =========================================================================
    # Content State
    # =========================================================================

    def _update_content_visibility(self) -> None:
        """Update the visible content state."""
        has_content = self._model.rowCount() > 0

        if has_content:
            self._content_layout.setCurrentWidget(self._table_view)
        else:
            self._content_layout.setCurrentWidget(self._message_label)

        self._edit_action.setEnabled(has_content)
        self._delete_action.setEnabled(has_content)

    # =========================================================================
    # UI Creation
    # =========================================================================

    def _create_title_label(self) -> QLabel:
        """Create the content overview title label.

        :returns: Configured title label.
        """
        title_label = QLabel(self._config.title, self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = QFont(title_label.font())
        font.setPointSize(self.TITLE_FONT_SIZE)
        font.setBold(True)

        title_label.setFont(font)

        return title_label

    def _create_message_label(self) -> QLabel:
        """Create the empty content message label.

        :returns: Configured empty content message label.
        """
        message_label = QLabel(self._config.empty_message, self)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)

        font = QFont(message_label.font())
        font.setPointSize(self.MESSAGE_FONT_SIZE)

        message_label.setFont(font)

        return message_label
