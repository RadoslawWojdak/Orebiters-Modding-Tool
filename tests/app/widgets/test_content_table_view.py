from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QTableView

from orebiters_modding_tool.app.models.table_sort_filter_proxy_model import (
    TableSortFilterProxyModel,
)
from orebiters_modding_tool.app.widgets.content_table_view import ContentTableView
from tests.app.helpers.table import ItemSample, ItemSampleTableModel, create_items


def create_table_view(items: list[ItemSample] | None = None) -> ContentTableView:
    """Create a content table view.

    :param items: Items displayed by the table.
    :returns: Configured content table view.
    """
    model = ItemSampleTableModel(items or create_items())
    proxy_model = TableSortFilterProxyModel(model)

    return ContentTableView(proxy_model)


def get_item_ids(table_view: ContentTableView) -> list[str]:
    """Return item IDs in table view order.

    :param table_view: Table view containing test items.
    :returns: Item IDs in table view order.
    """
    model = table_view.model()

    return [
        model.data(model.index(row, 0), Qt.ItemDataRole.DisplayRole)
        for row in range(model.rowCount())
    ]


def click_header_section(table_view: ContentTableView, section: int) -> None:
    """Click a table header section.

    :param table_view: Table view whose header should be clicked.
    :param section: Header section to click.
    """
    header = table_view.horizontalHeader()
    position = header.sectionViewportPosition(section)
    size = header.sectionSize(section)
    click_position = header.rect().center()
    click_position.setX(position + size // 2)

    QTest.mouseClick(header.viewport(), Qt.MouseButton.LeftButton, pos=click_position)


def test_initializes_table_view(qapp: QApplication) -> None:
    """Initialize the table view with its expected configuration."""
    table_view = create_table_view()

    assert table_view.alternatingRowColors()
    assert not table_view.isSortingEnabled()
    assert table_view.selectionBehavior() == QTableView.SelectionBehavior.SelectRows
    assert table_view.selectionMode() == QTableView.SelectionMode.ExtendedSelection
    assert table_view.editTriggers() == QTableView.EditTrigger.NoEditTriggers
    assert table_view.horizontalHeader().stretchLastSection()


def test_first_sortable_header_click_enables_sorting(qapp: QApplication) -> None:
    """Enable sorting after clicking a sortable column."""
    table_view = create_table_view()

    table_view._on_header_clicked(0)

    assert table_view.isSortingEnabled()


def test_first_sortable_header_click_sorts_ascending(qapp: QApplication) -> None:
    """Sort ascending after the first click on a sortable column."""
    table_view = create_table_view()

    table_view._on_header_clicked(0)

    assert get_item_ids(table_view) == ["x", "y", "z"]
    assert table_view.horizontalHeader().sortIndicatorSection() == 0
    assert table_view.horizontalHeader().sortIndicatorOrder() == Qt.SortOrder.AscendingOrder


def test_repeated_sortable_header_click_toggles_sort_order(qapp: QApplication) -> None:
    """Toggle sort order when clicking the same sortable column."""
    table_view = create_table_view()
    table_view.show()

    click_header_section(table_view, 0)
    click_header_section(table_view, 0)

    header = table_view.horizontalHeader()

    assert get_item_ids(table_view) == ["z", "y", "x"]
    assert header.sortIndicatorSection() == 0
    assert header.sortIndicatorOrder() == Qt.SortOrder.DescendingOrder


def test_clicking_different_sortable_column_sorts_ascending(qapp: QApplication) -> None:
    """Sort ascending when switching to another sortable column."""
    table_view = create_table_view()
    table_view.show()

    click_header_section(table_view, 0)
    click_header_section(table_view, 2)

    header = table_view.horizontalHeader()

    assert get_item_ids(table_view) == ["x", "z", "y"]
    assert header.sortIndicatorSection() == 2
    assert header.sortIndicatorOrder() == Qt.SortOrder.AscendingOrder


def test_clicking_non_sortable_column_does_not_change_sort(qapp: QApplication) -> None:
    """Keep the current sort when clicking a non-sortable column."""
    table_view = create_table_view()
    table_view.show()

    click_header_section(table_view, 0)
    click_header_section(table_view, 3)

    header = table_view.horizontalHeader()

    assert get_item_ids(table_view) == ["x", "y", "z"]
    assert header.sortIndicatorSection() == 0
    assert header.sortIndicatorOrder() == Qt.SortOrder.AscendingOrder


def test_clicking_non_sortable_column_before_sorting_does_not_enable_sorting(
    qapp: QApplication,
) -> None:
    """Keep sorting disabled when clicking a non-sortable column first."""
    table_view = create_table_view()
    table_view.show()

    click_header_section(table_view, 3)

    header = table_view.horizontalHeader()

    assert not table_view.isSortingEnabled()
    assert header.sortIndicatorSection() == -1
