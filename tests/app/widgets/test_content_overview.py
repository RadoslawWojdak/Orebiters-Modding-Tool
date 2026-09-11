from PySide6.QtCore import QSortFilterProxyModel

from orebiters_modding_tool.app.models.material_table_model import MaterialTableModel
from orebiters_modding_tool.app.widgets.content_overview_widget import (
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


def test_add_action_emits_add_requested(qapp) -> None:
    """Emit the content reference when adding content."""
    widget = create_widget([])

    received: list[ContentReference] = []
    widget.add_requested.connect(received.append)

    widget._add_action.trigger()

    assert received == [widget.content_reference]


def test_edit_action_does_nothing_without_selection(qapp) -> None:
    """Do not request editing without a selection."""
    widget = create_widget(create_materials())

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.edit_requested.connect(lambda reference, items: received.append((reference, items)))

    widget._edit_action.trigger()

    assert received == []


def test_edit_action_emits_selected_items(qapp) -> None:
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


def test_delete_action_does_nothing_without_selection(qapp) -> None:
    """Do not request deletion without a selection."""
    widget = create_widget(create_materials())

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.delete_requested.connect(lambda reference, items: received.append((reference, items)))

    widget._delete_action.trigger()

    assert received == []


def test_delete_action_emits_selected_items(qapp) -> None:
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


def test_double_click_emits_clicked_item(qapp) -> None:
    """Emit the double-clicked item for editing."""
    materials = create_materials()
    widget = create_widget(materials)

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.edit_requested.connect(lambda reference, items: received.append((reference, items)))

    index = widget._table_view.model().index(1, 0)
    widget._on_item_double_clicked(index)

    assert received == [(widget.content_reference, [materials[1]])]


def test_double_click_resolves_item_through_proxy_model(qapp) -> None:
    """Resolve the double-clicked item through a proxy model."""
    materials = create_materials()
    widget = create_widget(materials)

    proxy_model = QSortFilterProxyModel(widget)
    proxy_model.setSourceModel(widget.model)
    widget._table_view.setModel(proxy_model)

    received: list[tuple[ContentReference, list[Material]]] = []
    widget.edit_requested.connect(lambda reference, items: received.append((reference, items)))

    proxy_index = proxy_model.index(1, 0)
    widget._on_item_double_clicked(proxy_index)

    assert received == [(widget.content_reference, [materials[1]])]


def test_select_all_action_selects_all_rows(qapp) -> None:
    """Select all content rows."""
    widget = create_widget(create_materials())

    widget._select_all_action.trigger()

    selected_rows = widget._table_view.selectionModel().selectedRows()

    assert [index.row() for index in selected_rows] == [0, 1, 2]


def test_empty_model_shows_message_and_disables_edit_delete(qapp) -> None:
    """Show the empty message and disable content actions."""
    widget = create_widget([])

    assert widget._content_layout.currentWidget() is widget._message_label
    assert not widget._edit_action.isEnabled()
    assert not widget._delete_action.isEnabled()


def test_content_visibility_updates_when_model_changes(qapp) -> None:
    """Show the table when content is added."""
    widget = create_widget([])

    widget.model.add_item(MaterialFactory.create())

    assert widget._content_layout.currentWidget() is widget._table_view
    assert widget._edit_action.isEnabled()
    assert widget._delete_action.isEnabled()
