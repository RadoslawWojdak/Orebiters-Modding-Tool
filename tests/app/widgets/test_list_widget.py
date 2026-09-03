from unittest.mock import Mock

from PySide6.QtWidgets import QLabel, QPushButton

from orebiters_modding_tool.app.widgets.list_widget import ListWidget


class TestListWidget:
    """Tests for ListWidget."""

    def test_creates_widgets_for_initial_values(self, qapp: object) -> None:
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

    def test_shows_add_button(self, qapp: object) -> None:
        """Show the add button when can_add is enabled."""
        widget = ListWidget(
            item_factory=lambda: "new value",
            item_widget_factory=lambda value: QLabel(str(value)),
            values=[],
        )

        assert not widget._add_button.isHidden()

    def test_shows_remove_buttons(self, qapp: object) -> None:
        """Show remove buttons when can_remove is enabled."""
        widget = ListWidget(
            item_factory=lambda: "new value",
            item_widget_factory=lambda value: QLabel(str(value)),
            values=["first", "second"],
        )

        remove_buttons = [
            button for button in widget.findChildren(QPushButton) if button.text() == "Delete"
        ]

        assert len(remove_buttons) == 2
        assert all(not button.isHidden() for button in remove_buttons)

    def test_add_item_creates_new_item(self, qapp: object) -> None:
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

    def test_remove_item_removes_widget(self, qapp: object) -> None:
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

    def test_disabled_can_add_hides_add_button(self, qapp: object) -> None:
        """Hide the add button when the list has disabled can_add flag."""
        widget = ListWidget(
            item_factory=lambda: "new value",
            item_widget_factory=lambda value: QLabel(str(value)),
            values=[],
            can_add=False,
        )

        assert widget._add_button.isHidden()

    def test_disabled_can_remove_hides_remove_buttons(self, qapp: object) -> None:
        """Hide remove buttons when the list has disabled can_remove flag."""
        widget = ListWidget(
            item_factory=lambda: "new value",
            item_widget_factory=lambda value: QLabel(str(value)),
            values=["first", "second"],
            can_remove=False,
        )

        remove_buttons = [
            button for button in widget.findChildren(QPushButton) if button.text() == "Delete"
        ]

        assert len(remove_buttons) == 2
        assert all(button.isHidden() for button in remove_buttons)

    def test_disabled_can_add_does_not_add_item(self, qapp: object) -> None:
        """Do not add items when the list has disabled can_add flag."""
        item_factory = Mock(return_value="new value")

        widget = ListWidget(
            item_factory=item_factory,
            item_widget_factory=lambda value: QLabel(str(value)),
            values=[],
            can_add=False,
        )

        widget._add_item()

        assert widget._item_widgets == []
        item_factory.assert_not_called()

    def test_disabled_can_remove_does_not_remove_item(self, qapp: object) -> None:
        """Do not remove items when the list has disabled can_remove flag."""
        widget = ListWidget(
            item_factory=lambda: "new value",
            item_widget_factory=lambda value: QLabel(str(value)),
            values=["first"],
            can_remove=False,
        )

        item_widget = widget._item_widgets[0]
        row_widget = widget._items_layout.itemAt(0).widget()

        assert row_widget is not None

        widget._remove_item(row_widget, item_widget)

        assert widget._item_widgets == [item_widget]
        assert widget._items_layout.count() == 1
