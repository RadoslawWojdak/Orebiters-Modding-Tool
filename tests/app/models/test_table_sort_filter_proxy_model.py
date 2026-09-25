from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from orebiters_modding_tool.app.models.mineable_table_model import MineableTableModel
from orebiters_modding_tool.app.models.table_sort_filter_proxy_model import (
    TableSortFilterProxyModel,
)
from orebiters_modding_tool.domain.mineable import MineableType
from tests.app.helpers.table import ItemSample, ItemSampleTableModel, create_items
from tests.factories.mineable import MineableFactory


def create_proxy_model(items: list[ItemSample]) -> TableSortFilterProxyModel:
    """Create a table sort filter proxy model.

    :param items: Items displayed by the model.
    :returns: Configured proxy model.
    """
    model = ItemSampleTableModel(items)
    return TableSortFilterProxyModel(model)


def get_item_ids(proxy_model: TableSortFilterProxyModel) -> list[str]:
    """Return item IDs in proxy order.

    :param proxy_model: Proxy model containing test items.
    :returns: Item IDs in proxy order.
    """
    return [
        proxy_model.data(proxy_model.index(row, 0), Qt.ItemDataRole.DisplayRole)
        for row in range(proxy_model.rowCount())
    ]


# =============================================================================
# Sorting
# =============================================================================


def test_sort_ascending(qapp: QApplication) -> None:
    """Sort rows in ascending order."""
    proxy_model = create_proxy_model(create_items())

    proxy_model.sort(0, Qt.SortOrder.AscendingOrder)

    assert get_item_ids(proxy_model) == ["x", "y", "z"]


def test_sort_descending(qapp: QApplication) -> None:
    """Sort rows in descending order."""
    proxy_model = create_proxy_model(create_items())

    proxy_model.sort(0, Qt.SortOrder.DescendingOrder)

    assert get_item_ids(proxy_model) == ["z", "y", "x"]


def test_sort_by_different_columns(qapp: QApplication) -> None:
    """Sort rows using different columns."""
    proxy_model = create_proxy_model(create_items())

    proxy_model.sort(1, Qt.SortOrder.AscendingOrder)

    assert get_item_ids(proxy_model) == ["y", "z", "x"]

    proxy_model.sort(2, Qt.SortOrder.AscendingOrder)

    assert get_item_ids(proxy_model) == ["x", "z", "y"]


def test_sort_uses_sort_role_instead_of_display_role(qapp: QApplication) -> None:
    """Sort rows using the value provided by the sort role."""
    proxy_model = create_proxy_model(create_items())

    proxy_model.sort(1, Qt.SortOrder.AscendingOrder)

    assert get_item_ids(proxy_model) == ["y", "z", "x"]


def test_sort_is_case_insensitive(qapp: QApplication) -> None:
    """Sort values without considering letter case."""
    items = [
        ItemSample(id="a", name="orange", value=1, category="Z"),
        ItemSample(id="b", name="Apple", value=2, category="A"),
        ItemSample(id="c", name="BANANA", value=3, category="M"),
    ]
    proxy_model = create_proxy_model(items)

    proxy_model.sort(1, Qt.SortOrder.AscendingOrder)

    assert get_item_ids(proxy_model) == ["b", "c", "a"]


def test_sort_non_sortable_column_does_not_change_row_order(qapp: QApplication) -> None:
    """Do not change row order when sorting by a non-sortable column."""
    proxy_model = create_proxy_model(create_items())

    proxy_model.sort(3, Qt.SortOrder.AscendingOrder)

    assert get_item_ids(proxy_model) == ["y", "x", "z"]


def test_is_column_sortable_returns_column_configuration(qapp: QApplication) -> None:
    """Return whether a column can be sorted."""
    proxy_model = create_proxy_model(create_items())

    assert proxy_model.is_column_sortable(0)
    assert proxy_model.is_column_sortable(1)
    assert proxy_model.is_column_sortable(2)
    assert not proxy_model.is_column_sortable(3)


def test_sort_handles_none_values(qapp: QApplication) -> None:
    """Sort rows containing None values."""
    items = [
        ItemSample(id="a", name="Alpha", value=3, category="Z"),
        ItemSample(id="b", name="Bravo", value=1, category="A"),
        ItemSample(id="c", name="Charlie", value=2, category="M"),
    ]
    proxy_model = create_proxy_model(items)

    proxy_model.sort(1, Qt.SortOrder.AscendingOrder)

    assert get_item_ids(proxy_model) == ["a", "b", "c"]


def test_sort_handles_enum_values(qapp: QApplication) -> None:
    """Sort enum values using their underlying values."""
    mineables = [
        MineableFactory.create(id="resource", type=MineableType.RESOURCE),
        MineableFactory.create(id="artifact", type=MineableType.ARTIFACT),
        MineableFactory.create(id="obstacle", type=MineableType.OBSTACLE),
    ]
    proxy_model = TableSortFilterProxyModel(MineableTableModel(mineables))

    proxy_model.sort(2, Qt.SortOrder.AscendingOrder)

    assert [
        proxy_model.data(proxy_model.index(row, 0), Qt.ItemDataRole.DisplayRole)
        for row in range(proxy_model.rowCount())
    ] == ["artifact", "obstacle", "resource"]


def test_sort_handles_tuple_values(qapp: QApplication) -> None:
    """Sort tuple values using their individual elements."""
    mineables = [
        MineableFactory.create(id="deep", min_depth=10, max_depth=50),
        MineableFactory.create(id="shallow", min_depth=0, max_depth=100),
        MineableFactory.create(id="short", min_depth=10, max_depth=20),
    ]
    proxy_model = TableSortFilterProxyModel(MineableTableModel(mineables))

    proxy_model.sort(7, Qt.SortOrder.AscendingOrder)

    assert [
        proxy_model.data(proxy_model.index(row, 0), Qt.ItemDataRole.DisplayRole)
        for row in range(proxy_model.rowCount())
    ] == ["shallow", "short", "deep"]


# =============================================================================
# Filtering
# =============================================================================


def test_filter_text_is_empty_initially(qapp: QApplication) -> None:
    """Start with an empty filter text."""
    proxy_model = create_proxy_model(create_items())

    assert proxy_model.filter_text() == ""
    assert proxy_model.rowCount() == 3


def test_filter_matches_text_in_filterable_column(qapp: QApplication) -> None:
    """Show rows containing the filter text in a filterable column."""
    proxy_model = create_proxy_model(create_items())

    proxy_model.set_filter_text("Orange")

    assert get_item_ids(proxy_model) == ["x"]


def test_filter_is_case_insensitive(qapp: QApplication) -> None:
    """Filter values without considering letter case."""
    proxy_model = create_proxy_model(create_items())

    proxy_model.set_filter_text("orange")

    assert get_item_ids(proxy_model) == ["x"]


def test_filter_matches_multiple_columns(qapp: QApplication) -> None:
    """Match filter text against different filterable columns."""
    proxy_model = create_proxy_model(create_items())

    proxy_model.set_filter_text("2")

    assert get_item_ids(proxy_model) == ["z"]


def test_filter_ignores_non_filterable_columns(qapp: QApplication) -> None:
    """Ignore values from non-filterable columns."""
    proxy_model = create_proxy_model(create_items())

    proxy_model.set_filter_text("A1")

    assert get_item_ids(proxy_model) == []


def test_filter_returns_no_rows_when_nothing_matches(qapp: QApplication) -> None:
    """Return no rows when the filter matches nothing."""
    proxy_model = create_proxy_model(create_items())

    proxy_model.set_filter_text("Unknown")

    assert proxy_model.rowCount() == 0


def test_clearing_filter_restores_all_rows(qapp: QApplication) -> None:
    """Restore all rows after clearing the filter."""
    proxy_model = create_proxy_model(create_items())

    proxy_model.set_filter_text("Orange")
    assert proxy_model.rowCount() == 1

    proxy_model.set_filter_text("")

    assert get_item_ids(proxy_model) == ["y", "x", "z"]


def test_filter_text_is_trimmed(qapp: QApplication) -> None:
    """Trim whitespace from the filter text."""
    proxy_model = create_proxy_model(create_items())

    proxy_model.set_filter_text("  Orange  ")

    assert proxy_model.filter_text() == "Orange"
    assert get_item_ids(proxy_model) == ["x"]
