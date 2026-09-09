from unittest.mock import Mock

from PySide6.QtWidgets import QLabel, QPushButton

from orebiters_modding_tool.app.widgets.list_widget import ListWidget


def test_creates_widgets_for_initial_values(qapp: object) -> None:
    """Create a widget for every initial value."""
    item_widget_factory = Mock(side_effect=lambda value: QLabel(str(value)))

    widget = ListWidget(
        item_factory=lambda: "new value",
        item_widget_factory=item_widget_factory,
        values=["first", "second"],
    )

    assert len(widget._item_widgets) == 2
    item_widget_factory.assert_any_call("first")
    item_widget_factory.assert_any_call("second")


def test_enables_add_button_by_default(qapp: object) -> None:
    """Enable the add button by default."""
    widget = ListWidget(
        item_factory=lambda: "new value",
        item_widget_factory=lambda value: QLabel(str(value)),
        values=[],
    )

    assert widget._add_button.isEnabled()


def test_enables_remove_buttons_by_default(qapp: object) -> None:
    """Enable remove buttons by default."""
    widget = ListWidget(
        item_factory=lambda: "new value",
        item_widget_factory=lambda value: QLabel(str(value)),
        values=["first", "second"],
    )

    remove_buttons = [
        button for button in widget.findChildren(QPushButton) if button.text() == "Delete"
    ]

    assert len(remove_buttons) == 2
    assert all(button.isEnabled() for button in remove_buttons)


def test_add_item_creates_new_item(qapp: object) -> None:
    """Create and add a new item using the configured factory."""
    item_factory = Mock(return_value="new value")
    item_widget_factory = Mock(side_effect=lambda value: QLabel(str(value)))

    widget = ListWidget(
        item_factory=item_factory,
        item_widget_factory=item_widget_factory,
        values=[],
    )

    widget._add_item()

    assert len(widget._item_widgets) == 1
    item_factory.assert_called_once_with()
    item_widget_factory.assert_called_once_with("new value")


def test_remove_item_removes_widget(qapp: object) -> None:
    """Remove an existing item widget."""
    widget = ListWidget(
        item_factory=lambda: "new value",
        item_widget_factory=lambda value: QLabel(str(value)),
        values=["first"],
    )

    item_widget = widget._item_widgets[0]
    row_widget = widget._items_layout.itemAt(0).widget()

    assert row_widget is not None

    widget._remove_item(row_widget, item_widget)

    assert widget._item_widgets == []
    assert widget._items_layout.count() == 0


def test_disables_add_button_when_provider_returns_false(qapp: object) -> None:
    """Disable the add button when the provider returns false."""
    widget = ListWidget(
        item_factory=lambda: "new value",
        item_widget_factory=lambda value: QLabel(str(value)),
        values=[],
        can_add_provider=lambda: False,
    )

    assert not widget._add_button.isEnabled()


def test_disables_remove_buttons_when_provider_returns_false(qapp: object) -> None:
    """Disable remove buttons when the provider returns false."""
    widget = ListWidget(
        item_factory=lambda: "new value",
        item_widget_factory=lambda value: QLabel(str(value)),
        values=["first", "second"],
        can_remove_provider=lambda: False,
    )

    remove_buttons = [
        button for button in widget.findChildren(QPushButton) if button.text() == "Delete"
    ]

    assert len(remove_buttons) == 2
    assert all(not button.isEnabled() for button in remove_buttons)


def test_add_item_does_not_add_when_add_provider_returns_false(qapp: object) -> None:
    """Do not add an item when the provider returns false."""
    item_factory = Mock(return_value="new value")

    widget = ListWidget(
        item_factory=item_factory,
        item_widget_factory=lambda value: QLabel(str(value)),
        values=[],
        can_add_provider=lambda: False,
    )

    widget._add_item()

    assert widget._item_widgets == []
    item_factory.assert_not_called()


def test_remove_item_does_not_remove_when_remove_provider_returns_false(qapp: object) -> None:
    """Do not remove an item when the provider returns false."""
    widget = ListWidget(
        item_factory=lambda: "new value",
        item_widget_factory=lambda value: QLabel(str(value)),
        values=["first"],
        can_remove_provider=lambda: False,
    )

    item_widget = widget._item_widgets[0]
    row_widget = widget._items_layout.itemAt(0).widget()

    assert row_widget is not None

    widget._remove_item(row_widget, item_widget)

    assert widget._item_widgets == [item_widget]
    assert widget._items_layout.count() == 1


def test_refresh_updates_add_button(qapp: object) -> None:
    """Refresh the add button state."""
    can_add = True

    widget = ListWidget(
        item_factory=lambda: "new value",
        item_widget_factory=lambda value: QLabel(str(value)),
        values=[],
        can_add_provider=lambda: can_add,
    )

    assert widget._add_button.isEnabled()

    can_add = False
    widget.refresh()

    assert not widget._add_button.isEnabled()


def test_refresh_updates_remove_button(qapp: object) -> None:
    """Refresh the remove button state."""
    can_remove = True

    widget = ListWidget(
        item_factory=lambda: "new value",
        item_widget_factory=lambda value: QLabel(str(value)),
        values=["first", "second"],
        can_remove_provider=lambda: can_remove,
    )

    remove_buttons = [
        button for button in widget.findChildren(QPushButton) if button.text() == "Delete"
    ]

    assert len(remove_buttons) == 2
    assert all(button.isEnabled() for button in remove_buttons)

    can_remove = False
    widget.refresh()

    assert all(not button.isEnabled() for button in remove_buttons)
