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
from tests.factories.material import MaterialFactory


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

    widget = ContentOverviewWidget(
        content_reference=ContentReference(content_type=ContentType.MATERIALS),
        config=ContentOverviewConfig(
            title="Materials",
            empty_message="No materials found.",
        ),
        model=model,
    )
    widget.show()

    return widget


def test_add_action_emits_add_requested(qapp: QApplication) -> None:
    """Emit the content reference when adding content."""
    widget = create_widget([])

    received: list[ContentReference] = []
    widget.add_requested.connect(received.append)

    widget._add_action.trigger()

    assert received == [widget.content_reference]


def test_edit_action_does_nothing_without_selection(qapp: QApplication) -> None:
    """Do not request editing without a selection."""
    widget = create_widget(create_materials())

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.edit_requested.connect(lambda reference, items: received.append((reference, items)))

    widget._edit_action.trigger()

    assert received == []


def test_edit_action_emits_selected_items(qapp: QApplication) -> None:
    """Emit all selected items when editing."""
    materials = create_materials()
    widget = create_widget(materials)

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.edit_requested.connect(lambda reference, items: received.append((reference, items)))

    selection_model = widget._table_view.selectionModel()
    selection_model.select(
        widget.model.index(0, 0),
        selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows,
    )
    selection_model.select(
        widget.model.index(2, 0),
        selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows,
    )

    widget._edit_action.trigger()

    assert received == [(widget.content_reference, [materials[0], materials[2]])]


def test_delete_action_does_nothing_without_selection(qapp: QApplication) -> None:
    """Do not request deletion without a selection."""
    widget = create_widget(create_materials())

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.delete_requested.connect(lambda reference, items: received.append((reference, items)))

    widget._delete_action.trigger()

    assert received == []


def test_delete_action_emits_selected_items(qapp: QApplication) -> None:
    """Emit all selected items when deleting."""
    materials = create_materials()
    widget = create_widget(materials)

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.delete_requested.connect(lambda reference, items: received.append((reference, items)))

    selection_model = widget._table_view.selectionModel()
    selection_model.select(
        widget.model.index(1, 0),
        selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows,
    )

    widget._delete_action.trigger()

    assert received == [(widget.content_reference, [materials[1]])]


def test_double_click_emits_clicked_item(qapp: QApplication) -> None:
    """Emit the double-clicked item for editing."""
    materials = create_materials()
    widget = create_widget(materials)

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.edit_requested.connect(lambda reference, items: received.append((reference, items)))

    index = widget._table_view.model().index(1, 0)
    widget._on_item_double_clicked(index)

    assert received == [(widget.content_reference, [materials[1]])]


def test_double_click_resolves_item_through_proxy_model(qapp: QApplication) -> None:
    """Resolve the double-clicked item through the proxy model."""
    materials = create_materials()
    widget = create_widget(materials)

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.edit_requested.connect(lambda reference, items: received.append((reference, items)))

    proxy_index = widget._table_view.model().index(1, 0)
    widget._on_item_double_clicked(proxy_index)

    assert received == [(widget.content_reference, [materials[1]])]


def test_sorted_view_resolves_item_through_proxy_model(qapp: QApplication) -> None:
    """Resolve the correct item after sorting the view."""
    materials = create_materials()
    widget = create_widget(materials)

    proxy_model = widget._table_view.model()
    proxy_model.sort(0, Qt.SortOrder.AscendingOrder)

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.edit_requested.connect(lambda reference, items: received.append((reference, items)))

    proxy_index = proxy_model.index(0, 0)
    widget._on_item_double_clicked(proxy_index)

    assert received == [(widget.content_reference, [materials[1]])]


def test_select_all_action_selects_all_rows(qapp: QApplication) -> None:
    """Select all content rows."""
    widget = create_widget(create_materials())

    widget._select_all_action.trigger()

    selected_rows = widget._table_view.selectionModel().selectedRows()

    assert [index.row() for index in selected_rows] == [0, 1, 2]


def test_empty_model_shows_message_and_disables_edit_delete(qapp: QApplication) -> None:
    """Show the empty message and disable content actions."""
    widget = create_widget([])

    assert widget._content_layout.currentWidget() is widget._message_label
    assert not widget._edit_action.isEnabled()
    assert not widget._delete_action.isEnabled()


def test_content_visibility_updates_when_model_changes(qapp: QApplication) -> None:
    """Show the table when content is added."""
    widget = create_widget([])

    widget.model.add_item(MaterialFactory.create())

    assert widget._content_layout.currentWidget() is widget._table_view
    assert widget._edit_action.isEnabled()
    assert widget._delete_action.isEnabled()


def test_refresh_content_states_refreshes_model(qapp: QApplication) -> None:
    """Refresh content states through the content table model."""
    widget = create_widget(create_materials())

    with patch.object(widget.model, "refresh_content_states") as refresh_state:
        widget.refresh_content_states()

    refresh_state.assert_called_once()


# =============================================================================
# Filtering
# =============================================================================


def test_filter_edit_has_expected_configuration(qapp: QApplication) -> None:
    """Configure the filter input for content searching."""
    widget = create_widget(create_materials())

    assert widget._filter_edit.objectName() == "filter_edit"
    assert widget._filter_edit.placeholderText() == "Search materials..."
    assert widget._filter_edit.isClearButtonEnabled()


def test_filter_edit_filters_table_rows(qapp: QApplication) -> None:
    """Filter table rows using the filter input."""
    widget = create_widget(create_materials())

    widget._filter_edit.setText("copper")

    assert widget._table_view.model().rowCount() == 1
    assert (
        widget._table_view.model().data(
            widget._table_view.model().index(0, 0),
            Qt.ItemDataRole.DisplayRole,
        )
        == "copper_ore"
    )


def test_filter_edit_is_case_insensitive(qapp: QApplication) -> None:
    """Filter table rows without considering letter case."""
    widget = create_widget(create_materials())

    widget._filter_edit.setText("COPPER")

    assert widget._table_view.model().rowCount() == 1
    assert (
        widget._table_view.model().data(
            widget._table_view.model().index(0, 0),
            Qt.ItemDataRole.DisplayRole,
        )
        == "copper_ore"
    )


def test_filter_edit_can_match_multiple_rows(qapp: QApplication) -> None:
    """Show all rows matching the filter text."""
    materials = [
        MaterialFactory.create(id="iron_ore"),
        MaterialFactory.create(id="iron_ingot"),
        MaterialFactory.create(id="copper_ore"),
    ]
    widget = create_widget(materials)

    widget._filter_edit.setText("iron")

    proxy_model = widget._table_view.model()

    assert proxy_model.rowCount() == 2
    assert [
        proxy_model.data(proxy_model.index(row, 0), Qt.ItemDataRole.DisplayRole)
        for row in range(proxy_model.rowCount())
    ] == ["iron_ore", "iron_ingot"]


def test_clearing_filter_restores_all_rows(qapp: QApplication) -> None:
    """Restore all rows after clearing the filter."""
    widget = create_widget(create_materials())

    widget._filter_edit.setText("copper")

    assert widget._table_view.model().rowCount() == 1

    widget._filter_edit.clear()

    assert widget._table_view.model().rowCount() == 3


def test_filter_with_no_matches_keeps_table_visible(qapp: QApplication) -> None:
    """Keep the table visible when filtering produces no matches."""
    widget = create_widget(create_materials())

    widget._filter_edit.setText("unknown")

    assert widget._table_view.model().rowCount() == 0
    assert widget._content_layout.currentWidget() is widget._table_view
