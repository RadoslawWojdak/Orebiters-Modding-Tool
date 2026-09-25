from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QApplication, QTreeView

from orebiters_modding_tool.app.docks.project_explorer import ProjectExplorer
from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.services.project_service import ProjectService
from tests.factories.content import ContentReferenceFactory
from tests.factories.material import MaterialFactory


def generate_expected_rows() -> list[str]:
    return [content_type.display_name for content_type in ContentType]


def test_initializes_project_explorer(qapp: QApplication, project_service: ProjectService) -> None:
    """Initialize the Project Explorer with its expected UI structure."""
    explorer = ProjectExplorer(project_service)

    assert explorer.windowTitle() == ProjectExplorer.TITLE
    assert isinstance(explorer._tree_view, QTreeView)
    assert explorer.widget() is explorer._tree_view
    assert explorer._tree_view.model() is explorer._model
    assert explorer._tree_view.isHeaderHidden()
    assert not explorer._tree_view.expandsOnDoubleClick()


def test_create_item_creates_non_editable_item_with_content_reference(
    qapp: QApplication,
    project_service: ProjectService,
) -> None:
    """Create a non-editable item with its content reference."""
    explorer = ProjectExplorer(project_service)
    reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.iron")

    item = explorer._create_item("Iron", content_reference=reference)

    assert item.text() == "Iron"
    assert not item.isEditable()
    assert item.data(ProjectExplorer.CONTENT_TYPE_ROLE) == reference


def test_create_item_creates_non_editable_item_without_content_reference(
    qapp: QApplication,
    project_service: ProjectService,
) -> None:
    """Create a non-editable item without a content reference."""
    explorer = ProjectExplorer(project_service)

    item = explorer._create_item("Materials")

    assert item.text() == "Materials"
    assert not item.isEditable()
    assert item.data(ProjectExplorer.CONTENT_TYPE_ROLE) is None


def test_refresh_creates_all_content_categories(
    qapp: QApplication,
    project_service: ProjectService,
) -> None:
    """Create all content categories when refreshing the Project Explorer."""
    explorer = ProjectExplorer(project_service)

    expected_rows = generate_expected_rows()

    assert explorer._model.rowCount() == len(expected_rows)
    assert [
        explorer._model.item(row).text() for row in range(explorer._model.rowCount())
    ] == expected_rows


def test_refresh_creates_content_items_for_active_project(
    qapp: QApplication,
    active_project_service: ProjectService,
) -> None:
    """Create content items belonging to the active project."""
    active_project_service.add_content(ContentType.MATERIALS, MaterialFactory.create(id="iron"))
    active_project_service.add_content(ContentType.MATERIALS, MaterialFactory.create(id="copper"))

    explorer = ProjectExplorer(active_project_service)

    expected_rows = generate_expected_rows()
    materials_item = explorer._model.item(expected_rows.index("Materials"))

    assert materials_item is not None
    assert materials_item.text() == "Materials"
    assert materials_item.rowCount() == 2
    assert [materials_item.child(row).text() for row in range(materials_item.rowCount())] == [
        "copper",
        "iron",
    ]


def test_refresh_does_not_include_content_from_inactive_projects(
    qapp: QApplication,
    active_project_service: ProjectService,
) -> None:
    """Exclude content belonging to inactive projects."""
    first_project = active_project_service.active_project
    first_project_id = first_project.qualified_id

    active_project_service.add_content(ContentType.MATERIALS, MaterialFactory.create(id="iron"))
    active_project_service.save_project()

    active_project_service.create_project(namespace="other", name="Other Mod")
    project_ids = active_project_service.list_project_qualified_ids()
    second_project_id = next(
        project_id for project_id in project_ids if project_id != first_project_id
    )

    active_project_service.open_project(second_project_id)
    active_project_service.add_content(ContentType.MATERIALS, MaterialFactory.create(id="copper"))
    active_project_service.save_project()

    active_project_service.open_project(first_project.qualified_id)

    explorer = ProjectExplorer(active_project_service)

    expected_rows = generate_expected_rows()
    materials_item = explorer._model.item(expected_rows.index("Materials"))

    assert materials_item is not None
    assert materials_item.rowCount() == 1
    assert materials_item.child(0).text() == "iron"


def test_refresh_sorts_content_items_alphabetically(
    qapp: QApplication,
    active_project_service: ProjectService,
) -> None:
    """Sort content items alphabetically by their IDs."""
    for content_id in ("zinc", "copper", "iron", "aluminium"):
        active_project_service.add_content(
            ContentType.MATERIALS,
            MaterialFactory.create(id=content_id),
        )

    explorer = ProjectExplorer(active_project_service)

    expected_rows = generate_expected_rows()
    materials_item = explorer._model.item(expected_rows.index("Materials"))

    assert materials_item is not None
    assert [materials_item.child(row).text() for row in range(materials_item.rowCount())] == [
        "aluminium",
        "copper",
        "iron",
        "zinc",
    ]


def test_refresh_sorts_content_items_case_insensitively(
    qapp: QApplication,
    active_project_service: ProjectService,
) -> None:
    """Sort content items without considering letter case."""
    for content_id in ("zinc", "Copper", "aluminium", "Iron"):
        active_project_service.add_content(
            ContentType.MATERIALS,
            MaterialFactory.create(id=content_id),
        )

    explorer = ProjectExplorer(active_project_service)

    expected_rows = generate_expected_rows()
    materials_item = explorer._model.item(expected_rows.index("Materials"))

    assert materials_item is not None
    assert [materials_item.child(row).text() for row in range(materials_item.rowCount())] == [
        "aluminium",
        "Copper",
        "Iron",
        "zinc",
    ]


def test_get_active_project_references_returns_references_for_active_project(
    qapp: QApplication,
    active_project_service: ProjectService,
) -> None:
    """Return content references belonging to the active project."""
    active_project_service.add_content(ContentType.MATERIALS, MaterialFactory.create(id="iron"))

    explorer = ProjectExplorer(active_project_service)

    references = explorer._get_active_project_references(ContentType.MATERIALS)

    assert references == [
        ContentReference(
            content_type=ContentType.MATERIALS,
            qualified_id="test.test_mod.materials.iron",
        ),
    ]


def test_get_active_project_references_returns_empty_without_active_project(
    qapp: QApplication,
    project_service: ProjectService,
) -> None:
    """Return no content references when there is no active project."""
    explorer = ProjectExplorer(project_service)

    references = explorer._get_active_project_references(ContentType.MATERIALS)

    assert references == []


def test_content_reference_sort_key_returns_casefolded_content_id(
    qapp: QApplication,
    project_service: ProjectService,
) -> None:
    """Return a case-insensitive sort key for a content reference."""
    explorer = ProjectExplorer(project_service)
    reference = ContentReferenceFactory.create(qualified_id="test.test_mod.materials.Copper")

    assert explorer._content_reference_sort_key(reference) == "copper"


def test_double_click_emits_content_open_requested(
    qapp: QApplication,
    project_service: ProjectService,
) -> None:
    """Emit a content open request for an item with a content reference."""
    explorer = ProjectExplorer(project_service)

    item = explorer._create_item(
        "Iron",
        content_reference=ContentReferenceFactory.create(
            content_type=ContentType.MATERIALS,
            qualified_id="orebiters.core.materials.iron",
        ),
    )
    explorer._model.appendRow(item)

    index = explorer._model.indexFromItem(item)
    received_references: list[ContentReference] = []

    explorer.content_open_requested.connect(received_references.append)

    explorer._handle_item_double_clicked(index)

    assert received_references == [
        ContentReference(
            content_type=ContentType.MATERIALS, qualified_id="orebiters.core.materials.iron"
        ),
    ]


def test_double_click_emits_category_reference_for_content_category(
    qapp: QApplication,
    project_service: ProjectService,
    materials_category_reference: ContentReference,
) -> None:
    """Emit a category reference when double-clicking a content category."""
    explorer = ProjectExplorer(project_service)

    expected_rows = generate_expected_rows()
    materials_item = explorer._model.item(expected_rows.index("Materials"))

    assert materials_item is not None

    index = explorer._model.indexFromItem(materials_item)
    received_references: list[ContentReference] = []

    explorer.content_open_requested.connect(received_references.append)

    explorer._handle_item_double_clicked(index)

    assert received_references == [materials_category_reference]


def test_double_click_emits_content_reference_for_content_item(
    qapp: QApplication,
    active_project_service: ProjectService,
) -> None:
    """Emit a specific content reference when double-clicking a content item."""
    active_project_service.add_content(ContentType.MATERIALS, MaterialFactory.create(id="iron"))

    explorer = ProjectExplorer(active_project_service)

    expected_rows = generate_expected_rows()
    materials_item = explorer._model.item(expected_rows.index("Materials"))

    assert materials_item is not None

    content_item = materials_item.child(0)
    assert content_item is not None

    index = explorer._model.indexFromItem(content_item)
    received_references: list[ContentReference] = []

    explorer.content_open_requested.connect(received_references.append)

    explorer._handle_item_double_clicked(index)

    assert received_references == [
        ContentReference(
            content_type=ContentType.MATERIALS,
            qualified_id="test.test_mod.materials.iron",
        ),
    ]


def test_double_click_does_not_emit_for_item_without_content_reference(
    qapp: QApplication,
    project_service: ProjectService,
) -> None:
    """Ignore double clicks on items without a content reference."""
    explorer = ProjectExplorer(project_service)
    item = QStandardItem("Category without content")

    explorer._model.appendRow(item)

    index = explorer._model.indexFromItem(item)
    received_references: list[ContentReference] = []

    explorer.content_open_requested.connect(received_references.append)

    explorer._handle_item_double_clicked(index)

    assert received_references == []


def test_double_click_does_not_emit_for_invalid_index(
    qapp: QApplication,
    project_service: ProjectService,
) -> None:
    """Ignore double clicks for an invalid model index."""
    explorer = ProjectExplorer(project_service)
    received_references: list[ContentReference] = []

    explorer.content_open_requested.connect(received_references.append)

    explorer._handle_item_double_clicked(QModelIndex())

    assert received_references == []


def test_refresh_preserves_expanded_content_categories(
    qapp: QApplication,
    active_project_service: ProjectService,
) -> None:
    """Preserve expanded content categories when refreshing the Project Explorer."""
    active_project_service.add_content(ContentType.MATERIALS, MaterialFactory.create())

    explorer = ProjectExplorer(active_project_service)

    expected_rows = generate_expected_rows()
    materials_item = explorer._model.item(expected_rows.index("Materials"))

    assert materials_item is not None

    explorer._tree_view.expand(materials_item.index())
    assert explorer._tree_view.isExpanded(materials_item.index())

    explorer.refresh()

    refreshed_materials_item = explorer._model.item(expected_rows.index("Materials"))

    assert refreshed_materials_item is not None
    assert explorer._tree_view.isExpanded(refreshed_materials_item.index())


def test_get_expanded_categories_returns_expanded_content_types(
    qapp: QApplication,
    project_service: ProjectService,
) -> None:
    """Return content types of currently expanded categories."""
    explorer = ProjectExplorer(project_service)

    expected_rows = generate_expected_rows()
    materials_item = explorer._model.item(expected_rows.index("Materials"))
    mineables_item = explorer._model.item(expected_rows.index("Mineables"))

    assert materials_item is not None
    assert mineables_item is not None

    explorer._tree_view.expand(materials_item.index())
    explorer._tree_view.expand(mineables_item.index())

    assert explorer._get_expanded_categories() == {ContentType.MATERIALS, ContentType.MINEABLES}


def test_get_expanded_categories_ignores_collapsed_categories(
    qapp: QApplication,
    project_service: ProjectService,
) -> None:
    """Ignore content categories that are currently collapsed."""
    explorer = ProjectExplorer(project_service)

    expected_rows = generate_expected_rows()
    materials_item = explorer._model.item(expected_rows.index("Materials"))

    assert materials_item is not None

    assert explorer._get_expanded_categories() == set()


def test_restore_expanded_categories_expands_requested_content_types(
    qapp: QApplication,
    project_service: ProjectService,
) -> None:
    """Expand the requested content categories."""
    explorer = ProjectExplorer(project_service)

    explorer._restore_expanded_categories({ContentType.ITEMS, ContentType.MINEABLES})

    expected_rows = generate_expected_rows()
    items_item = explorer._model.item(expected_rows.index("Items"))
    materials_item = explorer._model.item(expected_rows.index("Materials"))
    mineables_item = explorer._model.item(expected_rows.index("Mineables"))

    assert items_item is not None
    assert materials_item is not None
    assert mineables_item is not None

    assert explorer._tree_view.isExpanded(items_item.index())
    assert not explorer._tree_view.isExpanded(materials_item.index())
    assert explorer._tree_view.isExpanded(mineables_item.index())
