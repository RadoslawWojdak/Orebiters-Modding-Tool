import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QPalette, QPixmap
from PySide6.QtWidgets import QApplication

from orebiters_modding_tool.app.delegates.content_table_delegate import ContentTableDelegate
from orebiters_modding_tool.app.models.column import Column
from orebiters_modding_tool.app.models.content_table_model import ContentTableModel
from orebiters_modding_tool.app.views.content_table_view import ContentTableView
from orebiters_modding_tool.domain.content import Content, ContentState
from tests.factories.content import ContentFactory


class ContentTableModelSample(ContentTableModel[Content]):
    """Table model used for testing the content table delegate."""

    COLUMNS = (
        Column(
            header="ID",
            getter=lambda item: item.id,
            setter=lambda item, value: setattr(item, "id", value),
            tooltip="Content ID",
        ),
    )


def create_model() -> ContentTableModelSample:
    """Create a test content table model."""
    return ContentTableModelSample([ContentFactory.create() for _ in range(4)])


def create_palette() -> QPalette:
    """Create a palette with distinct base colors."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#EEEEEE"))

    return palette


def render_table_view(table_view: ContentTableView) -> QPixmap:
    """Render a table view to a pixmap.

    :param table_view: Table view to render.
    :returns: Rendered table image.
    """
    table_view.resize(800, 400)
    table_view.show()
    QApplication.processEvents()

    pixmap = QPixmap(table_view.size())
    pixmap.fill(Qt.GlobalColor.transparent)
    table_view.render(pixmap)

    return pixmap


def get_cell_background(
    table_view: ContentTableView,
    pixmap: QPixmap,
    row: int,
    column: int = 0,
) -> QColor:
    """Return a background color sampled from a table cell.

    :param table_view: Table view containing the cell.
    :param pixmap: Rendered table image.
    :param row: Row containing the cell.
    :param column: Column containing the cell.
    :returns: Sampled cell background color.
    """
    index = table_view.model().index(row, column)
    rect = table_view.visualRect(index)

    point = QPoint(rect.right() - 5, rect.bottom() - 5)

    return pixmap.toImage().pixelColor(point)


def test_get_background_returns_base_for_saved_content_on_even_row(qapp: QApplication) -> None:
    """Return the base color for saved content on an even row."""
    model = create_model()
    index = model.index(0, 0)
    palette = create_palette()

    background = ContentTableDelegate._get_background(index, ContentState.SAVED, palette)

    assert background == palette.color(QPalette.ColorRole.Base)


def test_get_background_returns_alternate_base_for_saved_content_on_odd_row(
    qapp: QApplication,
) -> None:
    """Return the alternate base color for saved content on an odd row."""
    model = create_model()
    index = model.index(1, 0)
    palette = create_palette()

    background = ContentTableDelegate._get_background(index, ContentState.SAVED, palette)

    assert background == palette.color(QPalette.ColorRole.AlternateBase)


@pytest.mark.parametrize("state", [ContentState.NEW, ContentState.MODIFIED])
def test_get_background_tints_content_state(qapp: QApplication, state: ContentState) -> None:
    """Tint the background for content with a pending state."""
    model = create_model()
    index = model.index(0, 0)
    palette = create_palette()

    background = ContentTableDelegate._get_background(index, state, palette)

    assert background != palette.color(QPalette.ColorRole.Base)


@pytest.mark.parametrize("state", [ContentState.NEW, ContentState.MODIFIED])
def test_get_background_preserves_alternating_row_colors(
    qapp: QApplication,
    state: ContentState,
) -> None:
    """Preserve alternating row colors for content with a pending state."""
    model = create_model()
    even_index = model.index(0, 0)
    odd_index = model.index(1, 0)
    palette = create_palette()

    even_background = ContentTableDelegate._get_background(even_index, state, palette)
    odd_background = ContentTableDelegate._get_background(odd_index, state, palette)

    assert even_background != odd_background


def test_get_background_uses_different_colors_for_new_and_modified_content(
    qapp: QApplication,
) -> None:
    """Use different background colors for new and modified content."""
    model = create_model()
    index = model.index(0, 0)
    palette = create_palette()

    new_background = ContentTableDelegate._get_background(index, ContentState.NEW, palette)
    modified_background = ContentTableDelegate._get_background(
        index, ContentState.MODIFIED, palette
    )

    assert new_background != modified_background


def test_delegate_renders_different_content_states(qapp: QApplication) -> None:
    """Render different backgrounds for different content states."""
    model = create_model()
    table_view = ContentTableView(model)
    table_view.setItemDelegate(ContentTableDelegate(table_view))

    model.get_item(0).state = ContentState.SAVED
    saved_pixmap = render_table_view(table_view)
    saved_background = get_cell_background(table_view, saved_pixmap, 0)

    model.get_item(0).state = ContentState.NEW
    new_pixmap = render_table_view(table_view)
    new_background = get_cell_background(table_view, new_pixmap, 0)

    model.get_item(0).state = ContentState.MODIFIED
    modified_pixmap = render_table_view(table_view)
    modified_background = get_cell_background(table_view, modified_pixmap, 0)

    assert saved_background != new_background
    assert saved_background != modified_background
    assert new_background != modified_background


def test_delegate_preserves_alternating_row_colors_when_rendering(qapp: QApplication) -> None:
    """Preserve alternating row colors when rendering content states."""
    model = create_model()

    model.get_item(0).state = ContentState.NEW
    model.get_item(1).state = ContentState.NEW

    table_view = ContentTableView(model)
    table_view.setItemDelegate(ContentTableDelegate(table_view))

    pixmap = render_table_view(table_view)

    even_background = get_cell_background(table_view, pixmap, 0)
    odd_background = get_cell_background(table_view, pixmap, 1)

    assert even_background != odd_background


def test_delegate_renders_selection_overlay(qapp: QApplication) -> None:
    """Render a selection overlay for a selected item."""
    model = create_model()
    model.get_item(0).state = ContentState.MODIFIED

    table_view = ContentTableView(model)
    table_view.setItemDelegate(ContentTableDelegate(table_view))

    unselected_pixmap = render_table_view(table_view)
    unselected_background = get_cell_background(table_view, unselected_pixmap, 0)

    table_view.selectRow(0)

    selected_pixmap = render_table_view(table_view)
    selected_background = get_cell_background(table_view, selected_pixmap, 0)

    assert selected_background != unselected_background
