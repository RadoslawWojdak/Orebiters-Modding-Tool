from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QTableView
from pytestqt.qtbot import QtBot

from orebiters_modding_tool.app.delegates.content_table_delegate import ContentTableDelegate
from orebiters_modding_tool.app.models.table_sort_filter_proxy_model import (
    TableSortFilterProxyModel,
)
from orebiters_modding_tool.app.views.content_table_view import ContentTableView
from tests.app.helpers.table import ItemSample, ItemSampleTableModel, create_items


def create_table_view(items: list[ItemSample] | None = None) -> ContentTableView:
    """Create a content table view.

    :param items: Items displayed by the table.
    :returns: Configured content table view.
    """
    model = ItemSampleTableModel(items if items is not None else create_items())
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


def get_column_widths(table_view: ContentTableView) -> list[int]:
    """Return the widths of all table columns.

    :param table_view: Table whose column widths are measured.
    :returns: Column widths in logical column order.
    """
    return [table_view.columnWidth(column) for column in range(table_view.model().columnCount())]


def get_minimum_column_widths(table_view: ContentTableView) -> list[int]:
    """Return the minimum widths required by the table columns.

    :param table_view: Table whose column widths should be measured.
    :returns: Minimum width for each column.
    """
    header = table_view.horizontalHeader()

    return [header.sectionSizeHint(column) for column in range(table_view.model().columnCount())]


def get_minimum_table_width(table_view: ContentTableView) -> int:
    """Calculate the minimum table width required by its columns.

    :param table_view: Table whose minimum width should be calculated.
    :returns: Minimum total column width including the view frame.
    """
    minimum_column_widths = get_minimum_column_widths(table_view)
    frame_width = table_view.width() - table_view.viewport().width()

    return sum(minimum_column_widths) + frame_width


def show_table_view(qtbot: QtBot, table_view: ContentTableView) -> None:
    """Show the table view.

    :param qtbot: Qt test helper.
    :param table_view: Table view to show.
    """
    qtbot.addWidget(table_view)
    table_view.resize(1000, 400)
    table_view.show()


def wait_until_columns_fill_viewport(qtbot: QtBot, table_view: ContentTableView) -> None:
    """Wait until table columns fill the available viewport width.

    :param qtbot: Qt test helper.
    :param table_view: Table view to inspect.
    """
    qtbot.waitUntil(
        lambda: abs(sum(get_column_widths(table_view)) - table_view.viewport().width()) <= 1
    )


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
    header = table_view.horizontalHeader()

    assert table_view.alternatingRowColors()
    assert table_view.isSortingEnabled()
    assert table_view.selectionBehavior() == QTableView.SelectionBehavior.SelectRows
    assert table_view.selectionMode() == QTableView.SelectionMode.ExtendedSelection
    assert table_view.editTriggers() == QTableView.EditTrigger.NoEditTriggers
    assert not header.stretchLastSection()
    assert header.sortIndicatorSection() == -1
    assert isinstance(table_view.itemDelegate(), ContentTableDelegate)


def test_initializes_column_widths_when_shown(qtbot: QtBot) -> None:
    """Initialize column resizing when the view is shown."""
    table_view = create_table_view()
    show_table_view(qtbot, table_view)

    header = table_view.horizontalHeader()

    assert all(
        header.sectionResizeMode(column) == header.ResizeMode.Interactive
        for column in range(header.count())
    )


def test_empty_model_does_not_prevent_view_initialization(qtbot: QtBot) -> None:
    """Show a table with no rows without raising an error."""
    table_view = create_table_view([])
    show_table_view(qtbot, table_view)

    assert table_view.model().rowCount() == 0
    assert table_view.model().columnCount() > 0


def test_columns_fill_available_width(qtbot: QtBot) -> None:
    """Distribute available horizontal space across all columns."""
    table_view = create_table_view()
    show_table_view(qtbot, table_view)

    wait_until_columns_fill_viewport(qtbot, table_view)

    total_column_width = sum(get_column_widths(table_view))

    assert abs(total_column_width - table_view.viewport().width()) <= 1


def test_resizing_table_redistributes_column_widths(qtbot: QtBot) -> None:
    """Redistribute column widths when the table is resized."""
    table_view = create_table_view()
    show_table_view(qtbot, table_view)

    wait_until_columns_fill_viewport(qtbot, table_view)
    initial_widths = get_column_widths(table_view)

    table_view.resize(1200, 400)

    qtbot.waitUntil(
        lambda: abs(sum(get_column_widths(table_view)) - table_view.viewport().width()) <= 1
    )

    updated_widths = get_column_widths(table_view)

    assert updated_widths != initial_widths
    assert sum(updated_widths) > sum(initial_widths)


def test_resizing_table_preserves_minimum_column_widths(qtbot: QtBot) -> None:
    """Preserve minimum column widths when the table is narrowed."""
    table_view = create_table_view()
    show_table_view(qtbot, table_view)

    wait_until_columns_fill_viewport(qtbot, table_view)

    minimum_column_widths = get_minimum_column_widths(table_view)
    minimum_table_width = get_minimum_table_width(table_view)

    table_view.resize(max(1, minimum_table_width - 50), 400)

    qtbot.waitUntil(lambda: table_view.horizontalScrollBar().maximum() > 0)

    actual_widths = get_column_widths(table_view)

    for actual_width, minimum_width in zip(actual_widths, minimum_column_widths, strict=True):
        assert actual_width >= minimum_width


def test_narrow_table_allows_horizontal_scrolling(qtbot: QtBot) -> None:
    """Allow horizontal scrolling when columns exceed the viewport width."""
    table_view = create_table_view()
    show_table_view(qtbot, table_view)

    wait_until_columns_fill_viewport(qtbot, table_view)

    minimum_table_width = get_minimum_table_width(table_view)
    table_view.resize(max(1, minimum_table_width - 1), 400)

    qtbot.waitUntil(lambda: table_view.horizontalScrollBar().maximum() > 0)

    assert table_view.horizontalScrollBar().maximum() > 0


def test_first_sortable_header_click_sorts_ascending(qtbot: QtBot) -> None:
    """Sort ascending after the first click on a sortable column."""
    table_view = create_table_view()
    show_table_view(qtbot, table_view)

    click_header_section(table_view, 0)

    header = table_view.horizontalHeader()

    assert get_item_ids(table_view) == ["x", "y", "z"]
    assert header.sortIndicatorSection() == 0
    assert header.sortIndicatorOrder() == Qt.SortOrder.AscendingOrder


def test_repeated_sortable_header_click_toggles_sort_order(qtbot: QtBot) -> None:
    """Toggle sort order when clicking the same sortable column."""
    table_view = create_table_view()
    show_table_view(qtbot, table_view)

    click_header_section(table_view, 0)
    click_header_section(table_view, 0)

    header = table_view.horizontalHeader()

    assert get_item_ids(table_view) == ["z", "y", "x"]
    assert header.sortIndicatorSection() == 0
    assert header.sortIndicatorOrder() == Qt.SortOrder.DescendingOrder


def test_clicking_different_sortable_column_sorts_ascending(qtbot: QtBot) -> None:
    """Sort ascending when switching to another sortable column."""
    table_view = create_table_view()
    show_table_view(qtbot, table_view)

    click_header_section(table_view, 0)
    click_header_section(table_view, 2)

    header = table_view.horizontalHeader()

    assert get_item_ids(table_view) == ["x", "z", "y"]
    assert header.sortIndicatorSection() == 2
    assert header.sortIndicatorOrder() == Qt.SortOrder.AscendingOrder


def test_clicking_non_sortable_column_does_not_change_sort(qtbot: QtBot) -> None:
    """Keep the current sort when clicking a non-sortable column."""
    table_view = create_table_view()
    show_table_view(qtbot, table_view)

    click_header_section(table_view, 0)
    click_header_section(table_view, 3)

    header = table_view.horizontalHeader()

    assert get_item_ids(table_view) == ["x", "y", "z"]
    assert header.sortIndicatorSection() == 0
    assert header.sortIndicatorOrder() == Qt.SortOrder.AscendingOrder


def test_clicking_non_sortable_column_before_sorting_keeps_default_order(qtbot: QtBot) -> None:
    """Keep the default order when clicking a non-sortable column first."""
    table_view = create_table_view()
    show_table_view(qtbot, table_view)

    initial_order = get_item_ids(table_view)

    click_header_section(table_view, 3)

    header = table_view.horizontalHeader()

    assert table_view.isSortingEnabled()
    assert get_item_ids(table_view) == initial_order
    assert header.sortIndicatorSection() == -1
