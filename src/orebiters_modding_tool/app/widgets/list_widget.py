from collections.abc import Callable

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget


class ListWidget(QWidget):
    """Widget for managing a dynamic list of items."""

    def __init__(
        self,
        item_factory: Callable[[], object],
        item_widget_factory: Callable[[object], QWidget],
        values: list[object],
        parent: QWidget | None = None,
        *,
        can_add: bool = True,
        can_remove: bool = True,
    ) -> None:
        """Initialize the list widget.

        :param item_factory: Factory used to create new list items.
        :param item_widget_factory: Factory used to create item widgets.
        :param values: Initial list values.
        :param parent: Optional parent widget.
        :param read_only: Whether the list can be modified.
        """
        super().__init__(parent)

        self._item_factory = item_factory
        self._item_widget_factory = item_widget_factory
        self._can_add = can_add
        self._can_remove = can_remove
        self._item_widgets: list[QWidget] = []

        self._setup_layout()
        self._setup_items(values)

    def _setup_layout(self) -> None:
        """Set up the list layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._items_layout = QVBoxLayout()
        layout.addLayout(self._items_layout)

        self._add_button = QPushButton("Add", self)
        self._add_button.clicked.connect(self._add_item)

        layout.addWidget(self._add_button)

        self._add_button.setVisible(self._can_add)

    def _setup_items(self, values: list[object]) -> None:
        """Create widgets for existing list items.

        :param values: Initial list values.
        """
        for value in values:
            self._add_item_widget(value)

    def _add_item(self) -> None:
        """Create and add a new list item."""
        if not self._can_add:
            return

        value = self._item_factory()
        self._add_item_widget(value)

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
        self._items_layout.addWidget(row_widget)

        remove_button.setVisible(self._can_remove)

    def _remove_item(self, row_widget: QWidget, item_widget: QWidget) -> None:
        """Remove a list item widget.

        :param row_widget: Widget containing the item widget.
        :param item_widget: Editor widget to remove.
        """
        if not self._can_remove:
            return

        self._item_widgets.remove(item_widget)

        self._items_layout.removeWidget(row_widget)
        row_widget.deleteLater()
