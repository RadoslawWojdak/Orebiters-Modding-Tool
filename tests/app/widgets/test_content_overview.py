from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from orebiters_modding_tool.app.models.material_table_model import MaterialTableModel
from orebiters_modding_tool.app.widgets.content_overview import (
    ContentOverviewConfig,
    ContentOverviewWidget,
)
from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.material import Material
from tests.factories.material_factory import MaterialFactory


def create_materials() -> list[Material]:
    """Create test materials.

    :returns: Test materials.
    """
    return [
        MaterialFactory.create(id="iron_ore"),
        MaterialFactory.create(id="copper_ore"),
        MaterialFactory.create(id="gold_ore"),
    ]


def create_widget(materials: list[Material]) -> ContentOverviewWidget[Material]:
    """Create a content overview widget.

    :param materials: Materials displayed by the widget.
    :returns: Configured content overview widget.
    """
    model = MaterialTableModel(materials)

    return ContentOverviewWidget(
        content_reference=ContentReference(content_type=ContentType.MATERIALS),
        config=ContentOverviewConfig(
            title="Materials",
            empty_message="No materials found.",
        ),
        model=model,
    )


def show_widget(qtbot, widget: ContentOverviewWidget[Material]) -> None:
    """Show the widget and wait for table layout initialization.

    :param qtbot: Qt test helper.
    :param widget: Content overview widget.
    """
    qtbot.addWidget(widget)
    widget.resize(800, 500)
    widget.show()


def select_rows(widget: ContentOverviewWidget[Material], rows: list[int]) -> None:
    """Select table rows.

    :param widget: Content overview widget.
    :param rows: Row indices in the displayed table.
    """
    table_view = widget._table_view
    selection_model = table_view.selectionModel()

    for row in rows:
        index = table_view.model().index(row, 0)
        selection_model.select(
            index,
            selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows,
        )


def get_visible_item_ids(widget: ContentOverviewWidget[Material]) -> list[str]:
    """Return IDs of items currently displayed in the table.

    :param widget: Content overview widget.
    :returns: Visible item IDs in display order.
    """
    proxy_model = widget._table_view.model()

    return [
        proxy_model.data(proxy_model.index(row, 0), Qt.ItemDataRole.DisplayRole)
        for row in range(proxy_model.rowCount())
    ]


# =============================================================================
# Public API
# =============================================================================


def test_content_reference_returns_configured_reference(qapp: QApplication) -> None:
    """Expose the content reference represented by the widget."""
    widget = create_widget([])

    assert widget.content_reference == ContentReference(content_type=ContentType.MATERIALS)


def test_model_returns_configured_model(qapp: QApplication) -> None:
    """Expose the model used by the widget."""
    materials = create_materials()
    widget = create_widget(materials)

    assert widget.model.rowCount() == len(materials)


def test_refresh_content_states_refreshes_model(qapp: QApplication) -> None:
    """Refresh content states through the content table model."""
    widget = create_widget(create_materials())

    with patch.object(widget.model, "refresh_content_states") as refresh_state:
        widget.refresh_content_states()

    refresh_state.assert_called_once_with()


# =============================================================================
# Add
# =============================================================================


def test_add_action_emits_add_requested(qtbot) -> None:
    """Emit the content reference when adding content."""
    widget = create_widget([])
    show_widget(qtbot, widget)

    received: list[ContentReference] = []
    widget.add_requested.connect(received.append)

    widget._add_action.trigger()

    assert received == [widget.content_reference]


# =============================================================================
# Edit
# =============================================================================


def test_edit_action_does_nothing_without_selection(qtbot) -> None:
    """Do not request editing without a selection."""
    widget = create_widget(create_materials())
    show_widget(qtbot, widget)

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.edit_requested.connect(lambda reference, items: received.append((reference, items)))

    widget._edit_action.trigger()

    assert received == []


def test_edit_action_emits_selected_items(qtbot) -> None:
    """Emit selected items when editing."""
    materials = create_materials()
    widget = create_widget(materials)
    show_widget(qtbot, widget)

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.edit_requested.connect(lambda reference, items: received.append((reference, items)))

    select_rows(widget, [0, 2])
    widget._edit_action.trigger()

    assert received == [(widget.content_reference, [materials[0], materials[2]])]


def test_edit_action_emits_items_in_view_order(qtbot) -> None:
    """Emit selected items in the order of the displayed rows."""
    materials = create_materials()
    widget = create_widget(materials)
    show_widget(qtbot, widget)

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.edit_requested.connect(lambda reference, items: received.append((reference, items)))

    widget._table_view.model().sort(0, Qt.SortOrder.AscendingOrder)
    select_rows(widget, [0, 2])
    widget._edit_action.trigger()

    assert received == [(widget.content_reference, [materials[1], materials[0]])]


# =============================================================================
# Delete
# =============================================================================


def test_delete_action_does_nothing_without_selection(qtbot) -> None:
    """Do not request deletion without a selection."""
    widget = create_widget(create_materials())
    show_widget(qtbot, widget)

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.delete_requested.connect(lambda reference, items: received.append((reference, items)))

    widget._delete_action.trigger()

    assert received == []


def test_delete_action_emits_selected_items(qtbot) -> None:
    """Emit selected items when deleting."""
    materials = create_materials()
    widget = create_widget(materials)
    show_widget(qtbot, widget)

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.delete_requested.connect(lambda reference, items: received.append((reference, items)))

    select_rows(widget, [1])
    widget._delete_action.trigger()

    assert received == [(widget.content_reference, [materials[1]])]


# =============================================================================
# Double-click
# =============================================================================


def test_double_click_emits_clicked_item(qtbot) -> None:
    """Request editing the item double-clicked by the user."""
    materials = create_materials()
    widget = create_widget(materials)
    show_widget(qtbot, widget)

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.edit_requested.connect(lambda reference, items: received.append((reference, items)))

    table_view = widget._table_view
    index = table_view.model().index(1, 0)
    click_position = table_view.visualRect(index).center()

    assert table_view.visualRect(index).isValid()

    qtbot.mouseClick(table_view.viewport(), Qt.MouseButton.LeftButton, pos=click_position)
    qtbot.mouseDClick(table_view.viewport(), Qt.MouseButton.LeftButton, pos=click_position)

    assert received == [(widget.content_reference, [materials[1]])]


def test_double_click_resolves_item_after_sorting(qtbot) -> None:
    """Resolve the correct item after the displayed rows are sorted."""
    materials = create_materials()
    widget = create_widget(materials)
    show_widget(qtbot, widget)

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.edit_requested.connect(lambda reference, items: received.append((reference, items)))

    table_view = widget._table_view
    table_view.model().sort(0, Qt.SortOrder.AscendingOrder)

    index = table_view.model().index(0, 0)
    click_position = table_view.visualRect(index).center()

    qtbot.mouseClick(table_view.viewport(), Qt.MouseButton.LeftButton, pos=click_position)
    qtbot.mouseDClick(table_view.viewport(), Qt.MouseButton.LeftButton, pos=click_position)

    assert received == [(widget.content_reference, [materials[1]])]


# =============================================================================
# Select all
# =============================================================================


def test_select_all_action_selects_all_rows(qtbot) -> None:
    """Select all rows in the table."""
    widget = create_widget(create_materials())
    show_widget(qtbot, widget)

    widget._select_all_action.trigger()

    selected_rows = widget._table_view.selectionModel().selectedRows()

    assert len(selected_rows) == 3


# =============================================================================
# Content visibility
# =============================================================================


def test_empty_model_shows_message_and_disables_edit_delete(qapp: QApplication) -> None:
    """Show the empty message and disable content actions."""
    widget = create_widget([])

    assert widget._content_layout.currentWidget() is widget._message_label
    assert not widget._edit_action.isEnabled()
    assert not widget._delete_action.isEnabled()


def test_non_empty_model_shows_table_and_enables_edit_delete(qapp: QApplication) -> None:
    """Show the table and enable content actions when items exist."""
    widget = create_widget(create_materials())

    assert widget._content_layout.currentWidget() is widget._table_view
    assert widget._edit_action.isEnabled()
    assert widget._delete_action.isEnabled()


def test_content_visibility_updates_when_model_changes(qapp: QApplication) -> None:
    """Show the table when content is added."""
    widget = create_widget([])

    widget.model.add_item(MaterialFactory.create())

    assert widget._content_layout.currentWidget() is widget._table_view
    assert widget._edit_action.isEnabled()
    assert widget._delete_action.isEnabled()


def test_filtering_all_rows_does_not_show_empty_message(qapp: QApplication) -> None:
    """Keep the table visible when filtering produces no matches."""
    widget = create_widget(create_materials())

    widget._filter_edit.setText("unknown")

    assert widget._table_view.model().rowCount() == 0
    assert widget._content_layout.currentWidget() is widget._table_view


# =============================================================================
# Filtering
# =============================================================================


def test_filter_edit_has_expected_configuration(qapp: QApplication) -> None:
    """Configure the filter input for content searching."""
    widget = create_widget(create_materials())

    filter_edit = widget.findChild(
        __import__("PySide6.QtWidgets", fromlist=["QLineEdit"]).QLineEdit,
        "filter_edit",
    )

    assert filter_edit is not None
    assert filter_edit.placeholderText() == "Search materials..."
    assert filter_edit.isClearButtonEnabled()


def test_filter_edit_filters_table_rows(qapp: QApplication) -> None:
    """Filter table rows using the filter input."""
    widget = create_widget(create_materials())

    widget._filter_edit.setText("copper")

    assert get_visible_item_ids(widget) == ["copper_ore"]


def test_filter_edit_is_case_insensitive(qapp: QApplication) -> None:
    """Filter table rows without considering letter case."""
    widget = create_widget(create_materials())

    widget._filter_edit.setText("COPPER")

    assert get_visible_item_ids(widget) == ["copper_ore"]


def test_filter_edit_can_match_multiple_rows(qapp: QApplication) -> None:
    """Show all rows matching the filter text."""
    materials = [
        MaterialFactory.create(id="iron_ore"),
        MaterialFactory.create(id="iron_ingot"),
        MaterialFactory.create(id="copper_ore"),
    ]
    widget = create_widget(materials)

    widget._filter_edit.setText("iron")

    assert get_visible_item_ids(widget) == ["iron_ore", "iron_ingot"]


def test_clearing_filter_restores_all_rows(qapp: QApplication) -> None:
    """Restore all rows after clearing the filter."""
    widget = create_widget(create_materials())

    widget._filter_edit.setText("copper")
    assert len(get_visible_item_ids(widget)) == 1

    widget._filter_edit.clear()

    assert len(get_visible_item_ids(widget)) == 3


def test_filter_with_no_matches_keeps_table_visible(qapp: QApplication) -> None:
    """Keep the table visible when filtering produces no matches."""
    widget = create_widget(create_materials())

    widget._filter_edit.setText("unknown")

    assert get_visible_item_ids(widget) == []
    assert widget._content_layout.currentWidget() is widget._table_view
