from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QApplication, QTreeView

from orebiters_modding_tool.app.docks.project_explorer import ProjectExplorer
from orebiters_modding_tool.domain.content import ContentReference, ContentType


def test_initializes_project_explorer(qapp: QApplication) -> None:
    """Initialize the Project Explorer with its expected UI structure."""
    explorer = ProjectExplorer()

    assert explorer.windowTitle() == ProjectExplorer.TITLE
    assert isinstance(explorer._tree_view, QTreeView)
    assert explorer.widget() is explorer._tree_view
    assert explorer._tree_view.model() is explorer._model


def test_create_item_creates_non_editable_item_with_content_reference(qapp: QApplication) -> None:
    """Create a non-editable item with its content reference."""
    explorer = ProjectExplorer()
    reference = ContentReference(
        content_type=ContentType.MATERIALS,
        qualified_id="orebiters.core.iron",
    )

    item = explorer._create_item("Iron", content_reference=reference)

    assert item.text() == "Iron"
    assert not item.isEditable()
    assert item.data(ProjectExplorer.CONTENT_TYPE_ROLE) == reference


def test_create_item_creates_non_editable_item_without_content_reference(
    qapp: QApplication,
) -> None:
    """Create a non-editable item without a content reference."""
    explorer = ProjectExplorer()

    item = explorer._create_item("Materials")

    assert item.text() == "Materials"
    assert not item.isEditable()
    assert item.data(ProjectExplorer.CONTENT_TYPE_ROLE) is None


def test_double_click_emits_content_open_requested(qapp: QApplication) -> None:
    """Emit a content open request for an item with a content reference."""
    explorer = ProjectExplorer()

    item = explorer._create_item(
        "Iron",
        content_reference=ContentReference(
            content_type=ContentType.MATERIALS,
            qualified_id="orebiters.core.iron",
        ),
    )
    explorer._model.appendRow(item)

    index = explorer._model.indexFromItem(item)
    received_references: list[ContentReference] = []

    explorer.content_open_requested.connect(received_references.append)

    explorer._handle_item_double_clicked(index)

    assert received_references == [
        ContentReference(
            content_type=ContentType.MATERIALS,
            qualified_id="orebiters.core.iron",
        ),
    ]


def test_double_click_does_not_emit_for_item_without_content_reference(qapp: QApplication) -> None:
    """Ignore double clicks on items without a content reference."""
    explorer = ProjectExplorer()
    item = QStandardItem("Category without content")

    explorer._model.appendRow(item)

    index = explorer._model.indexFromItem(item)
    received_references: list[ContentReference] = []

    explorer.content_open_requested.connect(received_references.append)

    explorer._handle_item_double_clicked(index)

    assert received_references == []


def test_double_click_does_not_emit_for_invalid_index(qapp: QApplication) -> None:
    """Ignore double clicks for an invalid model index."""
    explorer = ProjectExplorer()
    received_references: list[ContentReference] = []

    explorer.content_open_requested.connect(received_references.append)

    explorer._handle_item_double_clicked(QModelIndex())

    assert received_references == []
