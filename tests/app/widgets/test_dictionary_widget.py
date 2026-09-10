from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from orebiters_modding_tool.app.widgets.dictionary_widget import DictionaryWidget


def test_creates_item_widget_for_each_dictionary_item(qapp: QApplication) -> None:
    """Create one item widget for each dictionary value."""
    items = {
        "first": "First value",
        "second": "Second value",
        "third": "Third value",
    }

    item_widget_factory = Mock(side_effect=lambda value: QLabel(str(value)))

    widget = DictionaryWidget(
        item_widget_factory=item_widget_factory,
        items=items,
    )

    assert item_widget_factory.call_count == 3
    assert set(widget._item_widgets) == set(items)

    assert widget._stacked_widget.count() == 3


def test_passes_dictionary_values_to_item_widget_factory(qapp: QApplication) -> None:
    """Pass each dictionary value to the item widget factory."""
    items = {
        "first": "First value",
        "second": "Second value",
    }

    item_widget_factory = Mock(side_effect=lambda value: QLabel(str(value)))

    DictionaryWidget(
        item_widget_factory=item_widget_factory,
        items=items,
    )

    assert item_widget_factory.call_args_list == [
        (("First value",), {}),
        (("Second value",), {}),
    ]


def test_stores_item_widgets_by_dictionary_key(qapp: QApplication) -> None:
    """Store each item widget using its dictionary key."""
    first_widget = QLabel("First")
    second_widget = QLabel("Second")

    item_widget_factory = Mock(side_effect=[first_widget, second_widget])

    widget = DictionaryWidget(
        item_widget_factory=item_widget_factory,
        items={
            "first": object(),
            "second": object(),
        },
    )

    assert widget._item_widgets["first"] is first_widget
    assert widget._item_widgets["second"] is second_widget


def test_creates_item_button_for_each_dictionary_item(qapp: QApplication) -> None:
    """Create one item button for each dictionary key."""
    items = {
        "first": object(),
        "second": object(),
        "third": object(),
    }

    widget = DictionaryWidget(
        item_widget_factory=lambda _value: QWidget(),
        items=items,
    )

    assert set(widget._item_buttons) == set(items)
    assert widget._item_buttons_layout.count() == len(items)


def test_uses_string_representation_as_default_item_label(qapp: QApplication) -> None:
    """Use string representations of keys as default item labels."""
    items = {
        1: object(),
        2: object(),
    }

    widget = DictionaryWidget(
        item_widget_factory=lambda _value: QWidget(),
        items=items,
    )

    assert widget._item_buttons[1].text() == "1"
    assert widget._item_buttons[2].text() == "2"


def test_uses_item_label_factory_for_button_labels(qapp: QApplication) -> None:
    """Create item button labels using the configured label factory."""
    items = {
        "first": object(),
        "second": object(),
    }

    item_label_factory = Mock(side_effect=lambda key: f"Item: {key}")

    widget = DictionaryWidget(
        item_widget_factory=lambda _value: QWidget(),
        items=items,
        item_label_factory=item_label_factory,
    )

    assert item_label_factory.call_args_list == [
        (("first",), {}),
        (("second",), {}),
    ]

    assert widget._item_buttons["first"].text() == "Item: first"
    assert widget._item_buttons["second"].text() == "Item: second"


def test_item_widgets_are_added_to_stacked_widget(qapp: QApplication) -> None:
    """Add all created item widgets to the stacked widget."""
    first_widget = QLabel("First")
    second_widget = QLabel("Second")

    widget = DictionaryWidget(
        item_widget_factory=Mock(side_effect=[first_widget, second_widget]),
        items={
            "first": object(),
            "second": object(),
        },
    )

    assert widget._stacked_widget.indexOf(first_widget) == 0
    assert widget._stacked_widget.indexOf(second_widget) == 1


def test_show_item_displays_widget_for_given_key(qapp: QApplication) -> None:
    """Display the item widget associated with the given key."""
    widget = DictionaryWidget(
        item_widget_factory=lambda value: QLabel(str(value)),
        items={
            "first": "First value",
            "second": "Second value",
        },
    )

    widget.show_item("second")

    assert widget._stacked_widget.currentWidget() is widget._item_widgets["second"]


def test_item_button_displays_associated_widget(qapp: QApplication) -> None:
    """Display the associated item widget when an item button is clicked."""
    widget = DictionaryWidget(
        item_widget_factory=lambda value: QLabel(str(value)),
        items={
            "first": "First value",
            "second": "Second value",
        },
    )

    widget._item_buttons["second"].click()

    assert widget._stacked_widget.currentWidget() is widget._item_widgets["second"]


def test_show_item_raises_key_error_for_unknown_key(qapp: QApplication) -> None:
    """Raise KeyError when attempting to display an unknown key."""
    widget = DictionaryWidget(
        item_widget_factory=lambda _value: QWidget(),
        items={"first": object()},
    )

    with pytest.raises(KeyError):
        widget.show_item("unknown")


def test_creates_empty_dictionary_widget(qapp: QApplication) -> None:
    """Create an empty widget when the dictionary has no items."""
    item_widget_factory = Mock()

    widget = DictionaryWidget(
        item_widget_factory=item_widget_factory,
        items={},
    )

    assert item_widget_factory.call_count == 0

    assert widget._item_widgets == {}
    assert widget._item_buttons == {}

    assert widget._item_buttons_layout.count() == 0
    assert widget._stacked_widget.count() == 0
