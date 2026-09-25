from dataclasses import dataclass

import pytest
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QApplication

from orebiters_modding_tool.app.models.base_table_model import BaseTableModel
from orebiters_modding_tool.app.models.column import Column


@dataclass
class Item:
    name: str
    value: int


class BaseTableModelSample(BaseTableModel[Item]):
    """Table model used for testing the base table model."""

    COLUMNS = (
        Column(
            header="Name",
            getter=lambda item: item.name,
            setter=lambda item, value: setattr(item, "name", value),
            tooltip="Item name",
        ),
        Column(
            header="Value",
            getter=lambda item: item.value,
            setter=lambda item, value: setattr(item, "value", value),
            tooltip="Item value",
            sorter=lambda item: -item.value,
        ),
        Column(
            header="Read-only",
            getter=lambda item: item.name.upper(),
            tooltip="Read-only value",
        ),
    )


def create_model() -> BaseTableModelSample:
    """Create a test table model."""
    return BaseTableModelSample(
        [
            Item("First", 10),
            Item("Second", 20),
        ],
    )


def test_initializes_with_items(qapp: QApplication) -> None:
    """Initialize the model with the provided items."""
    first_item = Item("First", 10)
    second_item = Item("Second", 20)

    model = BaseTableModelSample([first_item, second_item])

    assert model.rowCount() == 2
    assert model.get_item(0) is first_item
    assert model.get_item(1) is second_item


def test_row_count_returns_zero_for_valid_parent_index(qapp: QApplication) -> None:
    """Return zero rows for a valid parent index."""
    model = create_model()
    parent = model.index(0, 0)

    assert parent.isValid()
    assert model.rowCount(parent) == 0


def test_column_count_returns_number_of_columns(qapp: QApplication) -> None:
    """Return the number of configured columns."""
    model = create_model()

    assert model.columnCount() == 3


def test_column_count_returns_zero_for_valid_parent_index(qapp: QApplication) -> None:
    """Return zero columns for a valid parent index."""
    model = create_model()
    parent = model.index(0, 0)

    assert parent.isValid()
    assert model.columnCount(parent) == 0


def test_data_returns_display_and_edit_values(qapp: QApplication) -> None:
    """Return column values for display and edit roles."""
    model = create_model()

    name_index = model.index(0, 0)
    value_index = model.index(1, 1)

    assert model.data(name_index, Qt.ItemDataRole.DisplayRole) == "First"
    assert model.data(name_index, Qt.ItemDataRole.EditRole) == "First"
    assert model.data(value_index, Qt.ItemDataRole.DisplayRole) == 20
    assert model.data(value_index, Qt.ItemDataRole.EditRole) == 20


def test_data_returns_sort_value(qapp: QApplication) -> None:
    """Return the configured sort value for the sort role."""
    model = create_model()

    sorter_index = model.index(0, 1)
    getter_index = model.index(0, 0)

    assert model.data(sorter_index, BaseTableModel.SORT_ROLE) == -10
    assert model.data(getter_index, BaseTableModel.SORT_ROLE) == "First"


def test_data_returns_column_tooltip(qapp: QApplication) -> None:
    """Return the configured column tooltip."""
    model = create_model()
    index = model.index(0, 1)

    assert model.data(index, Qt.ItemDataRole.ToolTipRole) == "Item value"


def test_data_returns_none_for_invalid_index(qapp: QApplication) -> None:
    """Return no data for an invalid index."""
    model = create_model()

    assert model.data(QModelIndex()) is None


def test_data_returns_none_for_unsupported_role(qapp: QApplication) -> None:
    """Return no data for an unsupported role."""
    model = create_model()
    index = model.index(0, 0)

    assert model.data(index, Qt.ItemDataRole.UserRole + 1) is None


def test_header_data_returns_horizontal_header_and_tooltip(qapp: QApplication) -> None:
    """Return configured horizontal header data."""
    model = create_model()

    assert model.headerData(0, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) == "Name"
    assert (
        model.headerData(1, Qt.Orientation.Horizontal, Qt.ItemDataRole.ToolTipRole) == "Item value"
    )


def test_header_data_returns_none_for_vertical_orientation(qapp: QApplication) -> None:
    """Return no header data for vertical orientation."""
    model = create_model()

    assert model.headerData(0, Qt.Orientation.Vertical, Qt.ItemDataRole.DisplayRole) is None


def test_header_data_returns_none_for_invalid_section(qapp: QApplication) -> None:
    """Return no header data for an invalid section."""
    model = create_model()

    assert model.headerData(-1, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) is None
    assert model.headerData(3, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) is None


def test_header_data_returns_none_for_unsupported_role(qapp: QApplication) -> None:
    """Return no header data for an unsupported role."""
    model = create_model()

    assert model.headerData(0, Qt.Orientation.Horizontal, Qt.ItemDataRole.UserRole) is None


def test_flags_mark_editable_columns_as_editable(qapp: QApplication) -> None:
    """Mark columns with setters as editable."""
    model = create_model()

    editable_flags = model.flags(model.index(0, 0))
    read_only_flags = model.flags(model.index(0, 2))

    assert editable_flags & Qt.ItemFlag.ItemIsEnabled
    assert editable_flags & Qt.ItemFlag.ItemIsSelectable
    assert editable_flags & Qt.ItemFlag.ItemIsEditable

    assert read_only_flags & Qt.ItemFlag.ItemIsEnabled
    assert read_only_flags & Qt.ItemFlag.ItemIsSelectable
    assert not read_only_flags & Qt.ItemFlag.ItemIsEditable


def test_flags_return_no_flags_for_invalid_index(qapp: QApplication) -> None:
    """Return no flags for an invalid index."""
    model = create_model()

    assert model.flags(QModelIndex()) == Qt.ItemFlag.NoItemFlags


def test_set_data_updates_item(qapp: QApplication) -> None:
    """Update an item through an editable table cell."""
    model = create_model()
    index = model.index(0, 1)

    assert model.setData(index, 42)
    assert model.get_item(0).value == 42
    assert model.data(index, Qt.ItemDataRole.DisplayRole) == 42


def test_set_data_emits_data_changed(qapp: QApplication) -> None:
    """Emit dataChanged when an item is updated."""
    model = create_model()
    index = model.index(0, 0)
    changed_indexes: list[tuple[QModelIndex, QModelIndex, list[int]]] = []

    model.dataChanged.connect(
        lambda top_left, bottom_right, roles: changed_indexes.append(
            (top_left, bottom_right, roles),
        ),
    )

    assert model.setData(index, "Updated")

    assert changed_indexes == [
        (index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]),
    ]


def test_set_data_returns_false_for_invalid_index(qapp: QApplication) -> None:
    """Reject updates for an invalid index."""
    model = create_model()

    assert not model.setData(QModelIndex(), "Updated")


def test_set_data_returns_false_for_unsupported_role(qapp: QApplication) -> None:
    """Reject updates using a non-edit role."""
    model = create_model()
    index = model.index(0, 0)

    assert not model.setData(index, "Updated", Qt.ItemDataRole.DisplayRole)
    assert model.get_item(0).name == "First"


def test_set_data_returns_false_for_read_only_column(qapp: QApplication) -> None:
    """Reject updates for a column without a setter."""
    model = create_model()
    index = model.index(0, 2)

    assert not model.setData(index, "Updated")
    assert model.get_item(0).name == "First"


def test_get_item_returns_item_at_row(qapp: QApplication) -> None:
    """Return the item at the requested row."""
    model = create_model()

    assert model.get_item(0).name == "First"
    assert model.get_item(1).name == "Second"


def test_add_item_appends_item_to_model(qapp: QApplication) -> None:
    """Append an item to the model."""
    model = create_model()
    item = Item("Third", 30)

    model.add_item(item)

    assert model.rowCount() == 3
    assert model.get_item(2) is item


def test_remove_item_removes_and_returns_item(qapp: QApplication) -> None:
    """Remove and return a single item."""
    model = create_model()

    removed_item = model.remove_item(0)

    assert removed_item == Item("First", 10)
    assert model.rowCount() == 1
    assert model.get_item(0).name == "Second"


def test_remove_items_removes_and_returns_range(qapp: QApplication) -> None:
    """Remove and return a range of items."""
    model = BaseTableModelSample(
        [
            Item("First", 10),
            Item("Second", 20),
            Item("Third", 30),
            Item("Fourth", 40),
        ],
    )

    removed_items = model.remove_items(1, 2)

    assert removed_items == [Item("Second", 20), Item("Third", 30)]
    assert model.rowCount() == 2
    assert [model.get_item(row).name for row in range(model.rowCount())] == ["First", "Fourth"]


@pytest.mark.parametrize(
    ("first", "last"),
    [
        (-1, 0),
        (0, -1),
        (2, 1),
        (0, 2),
        (2, 3),
    ],
)
def test_remove_items_raises_for_invalid_range(qapp: QApplication, first: int, last: int) -> None:
    """Raise an error when removing an invalid range."""
    model = create_model()

    with pytest.raises(IndexError, match=f"Invalid range: {first}-{last}."):
        model.remove_items(first, last)
