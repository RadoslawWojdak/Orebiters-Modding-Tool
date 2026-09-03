from collections.abc import Callable, Mapping

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QStackedWidget, QVBoxLayout, QWidget


class DictionaryWidget(QWidget):
    """Widget for displaying dictionary items using stacked widgets."""

    def __init__(
        self,
        item_widget_factory: Callable[[object], QWidget],
        items: Mapping[object, object],
        item_label_factory: Callable[[object], str] = str,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the dictionary widget.

        :param item_widget_factory: Factory used to create item widgets.
        :param items: Dictionary items to display.
        :param item_label_factory: Factory used to create item button labels.
        :param parent: Optional parent widget.
        """
        super().__init__(parent)

        self._item_widget_factory = item_widget_factory
        self._item_label_factory = item_label_factory

        self._item_widgets: dict[object, QWidget] = {}
        self._item_buttons: dict[object, QPushButton] = {}

        self._setup_layout()
        self._setup_item_widgets(items)

    def show_item(self, key: object) -> None:
        """Display the widget associated with a dictionary key.

        :param key: Dictionary key of the item to display.
        :raises KeyError: If the key does not exist.
        """
        item_widget = self._item_widgets[key]

        self._stacked_widget.setCurrentWidget(item_widget)
        self.updateGeometry()

    def _setup_layout(self) -> None:
        """Set up the dictionary layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._item_buttons_layout = QHBoxLayout()
        layout.addLayout(self._item_buttons_layout)

        self._stacked_widget = QStackedWidget(self)
        layout.addWidget(self._stacked_widget)

    def _setup_item_widgets(self, items: Mapping[object, object]) -> None:
        """Create widgets for dictionary items.

        :param items: Dictionary items to display.
        """
        for key, value in items.items():
            self._add_item_widget(key, value)

    def _add_item_widget(self, key: object, value: object) -> None:
        """Create and add a widget for a dictionary item.

        :param key: Dictionary key.
        :param value: Dictionary value.
        """
        item_widget = self._item_widget_factory(value)

        item_button = QPushButton(self._item_label_factory(key), self)
        item_button.clicked.connect(lambda _checked=False, item_key=key: self.show_item(item_key))

        self._item_widgets[key] = item_widget
        self._item_buttons[key] = item_button

        self._stacked_widget.addWidget(item_widget)
        self._item_buttons_layout.addWidget(item_button)
