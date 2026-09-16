from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QMessageBox

from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget
from orebiters_modding_tool.app.editors.material_editor_widget import MaterialEditorWidget
from orebiters_modding_tool.app.models.material_table_model import MaterialTableModel
from orebiters_modding_tool.app.widgets.content_overview import ContentOverviewWidget
from orebiters_modding_tool.app.widgets.welcome_widget import WelcomeWidget
from orebiters_modding_tool.app.widgets.workspace import Workspace
from orebiters_modding_tool.domain.content import (
    ContentReference,
    ContentState,
    ContentType,
)
from orebiters_modding_tool.domain.material import Material
from tests.factories.content import ContentReferenceFactory
from tests.factories.material import MaterialFactory


def test_initializes_workspace(workspace: Workspace) -> None:
    """Initialize the workspace with its expected tab structure."""
    assert workspace._tab_widget.count() == 1
    assert isinstance(workspace._tab_widget.widget(0), WelcomeWidget)
    assert workspace._tab_widget.tabText(0) == "Welcome"
    assert workspace._tab_widget.tabsClosable()


def test_open_content_creates_content_tab(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Open a new content overview tab for a content category."""
    workspace.open_content(materials_category_reference)

    assert workspace._tab_widget.count() == 2
    assert workspace._tab_widget.currentIndex() == 1

    widget = workspace._tab_widget.currentWidget()
    assert isinstance(widget, ContentOverviewWidget)
    assert widget.content_reference == materials_category_reference
    assert workspace._tab_widget.tabText(1) == "Materials"


def test_open_content_activates_existing_content_tab(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Activate an existing content tab instead of opening a duplicate."""
    workspace.open_content(materials_category_reference)
    workspace._tab_widget.setCurrentIndex(0)

    workspace.open_content(materials_category_reference)

    assert workspace._tab_widget.count() == 2
    assert workspace._tab_widget.currentIndex() == 1


def test_open_content_creates_editor_for_specific_content(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Open an editor when opening a reference to specific content."""
    workspace.open_content(materials_category_reference)
    workspace._create_content(materials_category_reference, "iron_ore")

    project = workspace._project_service.active_project
    assert project is not None
    material = project.content[ContentType.MATERIALS][0]

    workspace._tab_widget.setCurrentIndex(0)

    workspace.open_content(
        ContentReferenceFactory.create(
            content_type=ContentType.MATERIALS,
            qualified_id=material.get_qualified_id(project.qualified_id),
        ),
    )

    current_widget = workspace._tab_widget.currentWidget()

    assert isinstance(current_widget, MaterialEditorWidget)
    assert current_widget.item is material


def test_open_content_activates_existing_editor_for_specific_content(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Activate an existing editor instead of opening a duplicate."""
    workspace.open_content(materials_category_reference)
    workspace._create_content(materials_category_reference, "iron_ore")

    project = workspace._project_service.active_project
    assert project is not None
    material = project.content[ContentType.MATERIALS][0]

    reference = ContentReferenceFactory.create(
        content_type=ContentType.MATERIALS,
        qualified_id=material.get_qualified_id(project.qualified_id),
    )

    initial_tab_count = workspace._tab_widget.count()

    workspace._tab_widget.setCurrentIndex(0)
    workspace.open_content(reference)
    workspace.open_content(reference)

    assert workspace._tab_widget.count() == initial_tab_count
    assert workspace._tab_widget.currentWidget() is workspace._tab_widget.widget(
        initial_tab_count - 1,
    )


def test_open_content_raises_for_missing_content(workspace: Workspace) -> None:
    """Raise an error when opening a reference to missing content."""
    reference = ContentReferenceFactory.create(qualified_id="test.test_mod.missing")

    with pytest.raises(ValueError, match="Content not found: test.test_mod.missing."):
        workspace.open_content(reference)


def test_open_content_raises_for_specific_content_without_active_project(
    workspace: Workspace,
) -> None:
    """Raise an error when opening specific content without an active project."""
    workspace._project_service.close_project()

    reference = ContentReferenceFactory.create()

    with pytest.raises(RuntimeError, match="No active project."):
        workspace.open_content(reference)


def test_create_content_model_returns_material_table_model(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Create a material table model for the materials content type."""
    model = workspace._create_content_model(materials_category_reference)

    assert isinstance(model, MaterialTableModel)


def test_create_content_model_raises_without_active_project(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Raise an error when creating a content model without an active project."""
    workspace._project_service.close_project()

    with pytest.raises(RuntimeError, match="No active project."):
        workspace._create_content_model(materials_category_reference)


def test_refresh_current_content_state_refreshes_current_content_tab(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Refresh the content state of the current content tab."""
    workspace.open_content(materials_category_reference)

    widget = workspace._tab_widget.currentWidget()
    assert isinstance(widget, ContentOverviewWidget)

    with patch.object(widget, "refresh_content_states") as refresh_state:
        workspace.refresh_current_content_state()

    refresh_state.assert_called_once()


def test_refresh_current_content_state_does_nothing_for_editor_tab(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Do nothing when the current tab is a content editor."""
    workspace.open_content(materials_category_reference)
    workspace._create_content(materials_category_reference, "iron_ore")

    editor = workspace._tab_widget.currentWidget()
    assert isinstance(editor, BaseEditorWidget)

    with patch.object(editor, "refresh") as refresh:
        workspace.refresh_current_content_state()

    refresh.assert_not_called()


@patch("orebiters_modding_tool.app.widgets.workspace.ContentIdDialog")
def test_add_content_opens_content_id_dialog(
    dialog_class: object,
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Open a content ID dialog for the requested content type."""
    workspace._add_content(materials_category_reference)

    dialog_class.assert_called_once()
    dialog_class.return_value.exec.assert_called_once()


def test_create_content_adds_item_to_project_model_and_editor(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Add content to the project, update its model, and open its editor."""
    project = workspace._project_service.active_project
    assert project is not None
    assert not project.has_unsaved_changes

    workspace.open_content(materials_category_reference)
    content_widget = workspace._get_content_widget(materials_category_reference)

    workspace._create_content(materials_category_reference, "iron_ore")

    materials = project.content[ContentType.MATERIALS]
    assert len(materials) == 1
    assert isinstance(materials[0], Material)
    assert materials[0].id == "iron_ore"
    assert project.has_unsaved_changes

    assert content_widget.model.rowCount() == 1
    assert content_widget.model.get_item(0) is materials[0]

    current_widget = workspace._tab_widget.currentWidget()
    assert isinstance(current_widget, BaseEditorWidget)
    assert current_widget.item is materials[0]


def test_create_content_emits_content_changed(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Emit a content change request after creating content."""
    workspace.open_content(materials_category_reference)

    received_references: list[ContentReference] = []
    workspace.content_changed.connect(received_references.append)

    workspace._create_content(materials_category_reference, "iron_ore")

    project = workspace._project_service.active_project
    assert project is not None

    assert received_references == [
        ContentReference(content_type=ContentType.MATERIALS, qualified_id="test.test_mod.iron_ore"),
    ]


def test_edit_content_opens_editor_for_new_item(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Open an editor for a content item without an existing editor."""
    material = MaterialFactory.create()

    workspace._edit_content(materials_category_reference, [material])

    current_widget = workspace._tab_widget.currentWidget()
    assert isinstance(current_widget, BaseEditorWidget)
    assert current_widget.item is material


def test_edit_content_opens_editor_without_duplicate(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Do not open duplicate editors for the same content."""
    workspace.open_content(materials_category_reference)
    workspace._create_content(materials_category_reference, "iron_ore")

    project = workspace._project_service.active_project
    assert project is not None
    material = project.content[ContentType.MATERIALS][0]

    initial_tab_count = workspace._tab_widget.count()

    workspace._edit_content(materials_category_reference, [material])
    workspace._edit_content(materials_category_reference, [material])

    assert workspace._tab_widget.count() == initial_tab_count

    editors = [
        workspace._tab_widget.widget(index)
        for index in range(workspace._tab_widget.count())
        if isinstance(workspace._tab_widget.widget(index), BaseEditorWidget)
    ]

    assert len(editors) == 1
    assert editors[0].item is material


def test_edit_content_opens_editors_for_multiple_items(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Open an editor for each selected content item."""
    workspace.open_content(materials_category_reference)
    workspace._create_content(materials_category_reference, "iron_ore")
    workspace._create_content(materials_category_reference, "copper_ore")

    project = workspace._project_service.active_project
    assert project is not None
    materials = project.content[ContentType.MATERIALS]

    workspace._edit_content(materials_category_reference, materials)

    editors = [
        workspace._tab_widget.widget(index)
        for index in range(workspace._tab_widget.count())
        if isinstance(workspace._tab_widget.widget(index), BaseEditorWidget)
    ]

    assert len(editors) == 2
    assert [editor.item for editor in editors] == materials


@patch(
    "orebiters_modding_tool.app.widgets.workspace.QMessageBox.question",
    return_value=QMessageBox.StandardButton.No,
)
def test_delete_content_keeps_items_when_deletion_is_cancelled(
    _mock_question: object,
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Keep content unchanged when deletion is canceled."""
    workspace.open_content(materials_category_reference)
    workspace._create_content(materials_category_reference, "iron_ore")

    project = workspace._project_service.active_project
    assert project is not None
    material = project.content[ContentType.MATERIALS][0]

    workspace._delete_content(materials_category_reference, [material])

    assert project.content[ContentType.MATERIALS] == [material]
    assert workspace._get_content_widget(materials_category_reference).model.rowCount() == 1
    assert workspace._find_editor_tab(material) is not None


@patch(
    "orebiters_modding_tool.app.widgets.workspace.QMessageBox.question",
    return_value=QMessageBox.StandardButton.Yes,
)
def test_delete_content_removes_item_closes_editor_and_updates_model(
    _mock_question: object,
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Delete content from the project and close its editor."""
    workspace.open_content(materials_category_reference)
    content_widget = workspace._get_content_widget(materials_category_reference)
    workspace._create_content(materials_category_reference, "iron_ore")

    project = workspace._project_service.active_project
    assert project is not None
    material = project.content[ContentType.MATERIALS][0]

    workspace._project_service.save_project()
    assert not project.has_unsaved_changes

    workspace._delete_content(materials_category_reference, [material])

    assert project.content[ContentType.MATERIALS] == []
    assert content_widget.model.rowCount() == 0
    assert workspace._find_editor_tab(material) is None
    assert project.has_unsaved_changes


@patch(
    "orebiters_modding_tool.app.widgets.workspace.QMessageBox.question",
    return_value=QMessageBox.StandardButton.Yes,
)
def test_delete_content_emits_content_changed(
    _mock_question: object,
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Emit a content change request after deleting content."""
    workspace.open_content(materials_category_reference)
    workspace._create_content(materials_category_reference, "iron_ore")

    project = workspace._project_service.active_project
    assert project is not None
    material = project.content[ContentType.MATERIALS][0]

    received_references: list[ContentReference] = []
    workspace.content_changed.connect(received_references.append)

    workspace._delete_content(materials_category_reference, [material])

    assert received_references == [materials_category_reference]


@patch(
    "orebiters_modding_tool.app.widgets.workspace.QMessageBox.question",
    return_value=QMessageBox.StandardButton.Yes,
)
def test_delete_content_ignores_items_missing_from_model(
    _mock_question: object,
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Ignore content items that are missing from the overview model."""
    workspace.open_content(materials_category_reference)
    content_widget = workspace._get_content_widget(materials_category_reference)

    item = MaterialFactory.create()

    workspace._delete_content(materials_category_reference, [item])

    assert content_widget.model.rowCount() == 0


def test_close_project_tabs_closes_project_tabs_and_keeps_welcome(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Close project tabs without closing the Welcome tab."""
    workspace.open_content(materials_category_reference)
    workspace._create_content(materials_category_reference, "iron_ore")

    workspace.close_project_tabs()

    assert workspace._tab_widget.count() == 1
    assert workspace._tab_widget.tabText(0) == "Welcome"


def test_create_content_item_creates_material(
    materials_category_reference: ContentReference,
) -> None:
    """Create a material with default localizations and crafting materials."""
    item = Workspace._create_content_item(materials_category_reference, "iron_ore")

    assert isinstance(item, Material)
    assert item.id == "iron_ore"
    assert set(item.localizations) == {"en", "pl"}
    assert item.crafting_materials == []
    assert item.state is ContentState.NEW


def test_create_content_item_raises_for_unsupported_content_type() -> None:
    """Raise an error when creating an unsupported content type."""
    reference = ContentReference(content_type=ContentType.ITEMS)

    with pytest.raises(ValueError, match="Unsupported content type"):
        Workspace._create_content_item(reference, "sword")


def test_create_content_editor_creates_material_editor(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Create a material editor for a material item."""
    item = MaterialFactory.create()

    editor = workspace._create_content_editor(materials_category_reference, item)

    assert isinstance(editor, MaterialEditorWidget)
    assert editor.item is item


def test_create_content_editor_raises_for_invalid_material(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Raise an error when creating a material editor for an invalid item."""
    item = object()

    with pytest.raises(TypeError, match="Expected a Material."):
        workspace._create_content_editor(materials_category_reference, item)  # type: ignore[arg-type]


def test_create_content_editor_raises_for_unsupported_content_type(
    workspace: Workspace,
) -> None:
    """Raise an error when creating an editor for an unsupported content type."""
    reference = ContentReference(content_type=ContentType.ITEMS)

    with pytest.raises(ValueError, match="Unsupported content type"):
        workspace._create_content_editor(reference, object())  # type: ignore[arg-type]


def test_create_content_editor_connects_saved_signal(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Emit a content change when the created editor is saved."""
    project = workspace._project_service.active_project
    assert project is not None
    assert not project.has_unsaved_changes

    item = MaterialFactory.create(id="iron_ore", state=ContentState.SAVED)

    editor = workspace._create_content_editor(materials_category_reference, item)

    received_references: list[ContentReference] = []
    workspace.content_changed.connect(received_references.append)

    editor.saved.emit()

    assert received_references == [
        ContentReference(content_type=ContentType.MATERIALS, qualified_id="test.test_mod.iron_ore"),
    ]
    assert item.state is ContentState.MODIFIED
    assert project.has_unsaved_changes


def test_saving_content_emits_updated_content_reference(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Emit the updated content reference when saving edited content."""
    workspace.open_content(materials_category_reference)
    workspace._create_content(materials_category_reference, "iron_ore")

    project = workspace._project_service.active_project
    assert project is not None
    material = project.content[ContentType.MATERIALS][0]

    editor = workspace._find_editor_tab(material)
    assert editor is not None
    assert isinstance(workspace._tab_widget.widget(editor), BaseEditorWidget)

    editor_widget = workspace._tab_widget.widget(editor)
    assert isinstance(editor_widget, BaseEditorWidget)

    received_references: list[ContentReference] = []
    workspace.content_changed.connect(received_references.append)

    material.id = "refined_iron"

    editor_widget.saved.emit()

    assert received_references[-1] == ContentReference(
        content_type=ContentType.MATERIALS,
        qualified_id="test.test_mod.refined_iron",
    )


def test_saving_saved_content_marks_it_as_modified(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Mark saved content as modified after editor save."""
    item = MaterialFactory.create(state=ContentState.SAVED)

    project = workspace._project_service.active_project
    assert project is not None
    assert not project.has_unsaved_changes

    workspace._handle_content_editor_saved(materials_category_reference, item)

    assert item.state is ContentState.MODIFIED
    assert project.has_unsaved_changes


def test_saving_new_content_keeps_it_new(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Keep new content marked as new after editor save."""
    item = MaterialFactory.create(state=ContentState.NEW)

    project = workspace._project_service.active_project
    assert project is not None
    assert not project.has_unsaved_changes

    workspace._handle_content_editor_saved(materials_category_reference, item)

    assert item.state is ContentState.NEW
    assert project.has_unsaved_changes


def test_create_material_editor_context_contains_project_information(workspace: Workspace) -> None:
    """Create material editor context from the active project."""
    context = workspace._create_material_editor_context()

    project = workspace._project_service.active_project
    assert project is not None

    assert context["mod_id"] == project.qualified_id
    assert callable(context["material_references_provider"])


def test_create_material_editor_context_raises_without_active_project(workspace: Workspace) -> None:
    """Raise an error when creating editor context without an active project."""
    workspace._project_service.close_project()

    with pytest.raises(RuntimeError, match="No active project."):
        workspace._create_material_editor_context()


def test_create_content_reference_returns_reference_to_content(workspace: Workspace) -> None:
    """Create a reference to content in the active project."""
    item = MaterialFactory.create(id="iron_ore")
    reference = workspace._create_content_reference(ContentType.MATERIALS, item)

    project = workspace._project_service.active_project
    assert project is not None

    assert reference == ContentReference(
        content_type=ContentType.MATERIALS,
        qualified_id=f"{project.qualified_id}.iron_ore",
    )


def test_create_content_reference_raises_without_active_project(workspace: Workspace) -> None:
    """Raise an error when creating a content reference without an active project."""
    workspace._project_service.close_project()

    item = MaterialFactory.create()

    with pytest.raises(RuntimeError, match="No active project."):
        workspace._create_content_reference(ContentType.MATERIALS, item)


def test_get_content_widget_returns_open_content_widget(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Return the open content widget for a content reference."""
    workspace.open_content(materials_category_reference)

    widget = workspace._get_content_widget(materials_category_reference)

    assert isinstance(widget, ContentOverviewWidget)
    assert widget.content_reference == materials_category_reference


def test_get_content_widget_raises_for_closed_content_tab(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Raise an error when the requested content tab is not open."""
    with pytest.raises(RuntimeError, match="Content tab is not open"):
        workspace._get_content_widget(materials_category_reference)


def test_find_item_row_returns_matching_item_row() -> None:
    """Return the row containing the requested item."""
    item = MaterialFactory.create()
    other_item = MaterialFactory.create()

    model = MaterialTableModel([item, other_item])

    assert Workspace._find_item_row(model, other_item) == 1


def test_find_item_row_returns_none_for_missing_item() -> None:
    """Return none when the requested item is not in the model."""
    item = MaterialFactory.create()
    model = MaterialTableModel([item])

    missing_item = MaterialFactory.create()

    assert Workspace._find_item_row(model, missing_item) is None


def test_switching_to_editor_tab_refreshes_editor(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Refresh the editor when switching to its tab."""
    workspace.open_content(materials_category_reference)
    workspace._create_content(materials_category_reference, "iron_ore")

    editor = workspace._tab_widget.currentWidget()
    assert isinstance(editor, BaseEditorWidget)

    with patch.object(editor, "refresh") as refresh:
        workspace._tab_widget.setCurrentIndex(0)
        workspace._tab_widget.setCurrentWidget(editor)

    refresh.assert_called_once()


def test_find_content_tab_returns_matching_tab(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Return the tab index for an open content reference."""
    workspace.open_content(materials_category_reference)

    assert workspace._find_content_tab(materials_category_reference) == 1


def test_find_content_tab_returns_none_for_missing_tab(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Return none when a content reference is not open."""
    assert workspace._find_content_tab(materials_category_reference) is None


def test_close_editor_tab_closes_matching_editor(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Close the editor tab for a content item."""
    workspace.open_content(materials_category_reference)
    workspace._create_content(materials_category_reference, "iron_ore")

    project = workspace._project_service.active_project
    assert project is not None
    material = project.content[ContentType.MATERIALS][0]

    workspace._close_editor_tab(material)

    assert workspace._find_editor_tab(material) is None


def test_close_editor_tab_ignores_missing_editor(workspace: Workspace) -> None:
    """Ignore requests to close a content item without an open editor."""
    item = MaterialFactory.create()

    workspace._close_editor_tab(item)

    assert workspace._tab_widget.count() == 1


def test_find_editor_tab_returns_matching_editor(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Return the tab index for an open content editor."""
    workspace.open_content(materials_category_reference)
    workspace._create_content(materials_category_reference, "iron_ore")

    project = workspace._project_service.active_project
    assert project is not None
    material = project.content[ContentType.MATERIALS][0]

    index = workspace._find_editor_tab(material)

    assert index is not None
    assert isinstance(workspace._tab_widget.widget(index), BaseEditorWidget)


def test_find_editor_tab_returns_none_for_missing_editor(workspace: Workspace) -> None:
    """Return none when a content editor is not open."""
    item = MaterialFactory.create()

    assert workspace._find_editor_tab(item) is None


def test_get_editor_tab_name_returns_item_id() -> None:
    """Return the content ID as the editor tab name."""
    item = MaterialFactory.create(id="iron_ore")

    assert Workspace._get_editor_tab_name(item) == "iron_ore"


def test_get_tab_name_returns_content_type_for_category_reference(
    materials_category_reference: ContentReference,
) -> None:
    """Return the content type name for a category reference."""
    assert Workspace._get_tab_name(materials_category_reference) == "Materials"


def test_get_tab_name_returns_content_type_and_content_id() -> None:
    """Return the content type name and content ID for a content reference."""
    reference = ContentReferenceFactory.create(
        content_type=ContentType.MATERIALS,
        qualified_id="orebiters.core.iron",
    )

    assert Workspace._get_tab_name(reference) == "Materials iron"
