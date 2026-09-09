from collections.abc import Callable

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

CanOperationProvider = Callable[[], bool]


class ListWidget(QWidget):
    """Widget for managing a dynamic list of items."""

    def __init__(
        self,
        item_factory: Callable[[], object],
        item_widget_factory: Callable[[object], QWidget],
        values: list[object],
        parent: QWidget | None = None,
        *,
        can_add_provider: CanOperationProvider | None = None,
        can_remove_provider: CanOperationProvider | None = None,
    ) -> None:
        """Initialize the list widget.

        :param item_factory: Factory used to create new list items.
        :param item_widget_factory: Factory used to create item widgets.
        :param values: Initial list values.
        :param parent: Optional parent widget.
        :param can_add_provider: Provides whether items can be added.
        :param can_remove_provider: Provides whether items can be removed.
        """
        super().__init__(parent)

        self._item_factory = item_factory
        self._item_widget_factory = item_widget_factory
        self._can_add_provider = can_add_provider
        self._can_remove_provider = can_remove_provider
        self._item_widgets: list[QWidget] = []
        self._remove_buttons: list[QPushButton] = []

        self._setup_layout()
        self._setup_items(values)
        self.refresh()

    def item_count(self) -> int:
        """Return the number of items."""
        return len(self._item_widgets)

    def item_at(self, index: int) -> QWidget:
        """Return the widget at the given item index."""
        return self._item_widgets[index]

    def refresh(self) -> None:
        """Refresh operation button states."""
        self._update_add_button()
        self._update_remove_buttons()

    def _setup_layout(self) -> None:
        """Set up the list layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._items_layout = QVBoxLayout()
        layout.addLayout(self._items_layout)

        self._add_button = QPushButton("Add", self)
        self._add_button.clicked.connect(self._add_item)

        layout.addWidget(self._add_button)

    def _setup_items(self, values: list[object]) -> None:
        """Create widgets for existing list items.

        :param values: Initial list values.
        """
        for value in values:
            self._add_item_widget(value)

    def _add_item(self) -> None:
        """Create and add a new list item."""
        if not self._can_add():
            return

        value = self._item_factory()
        self._add_item_widget(value)
        self.refresh()

    def _add_item_widget(self, value: object) -> None:
        """Create and add a widget for a list item.

        :param value: List item value.
        """
        item_widget = self._item_widget_factory(value)

        row_widget = QWidget(self)
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)

        row_layout.addWidget(item_widget)

        remove_button = QPushButton("Delete", row_widget)
        remove_button.clicked.connect(lambda: self._remove_item(row_widget, item_widget))

        row_layout.addWidget(remove_button)

        self._item_widgets.append(item_widget)
        self._remove_buttons.append(remove_button)
        self._items_layout.addWidget(row_widget)

    def _remove_item(self, row_widget: QWidget, item_widget: QWidget) -> None:
        """Remove a list item widget.

        :param row_widget: Widget containing the item widget.
        :param item_widget: Editor widget to remove.
        """
        if not self._can_remove():
            return

        self._item_widgets.remove(item_widget)

        remove_button = row_widget.findChild(QPushButton)
        if remove_button is not None:
            self._remove_buttons.remove(remove_button)

        self._items_layout.removeWidget(row_widget)
        row_widget.deleteLater()

        self.refresh()

    def _can_add(self) -> bool:
        """Check whether an item can be added."""
        if self._can_add_provider is None:
            return True

        return self._can_add_provider()

    def _can_remove(self) -> bool:
        """Check whether an item can be removed."""
        if self._can_remove_provider is None:
            return True

        return self._can_remove_provider()

    def _update_add_button(self) -> None:
        """Update the add button state."""
        self._add_button.setEnabled(self._can_add())

    def _update_remove_buttons(self) -> None:
        """Update the remove button states."""
        can_remove = self._can_remove()

        for button in self._remove_buttons:
            button.setEnabled(can_remove)
