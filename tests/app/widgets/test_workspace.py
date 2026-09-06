from unittest.mock import patch

from PySide6.QtWidgets import QMessageBox

from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget
from orebiters_modding_tool.app.widgets.content_overview_widget import ContentOverviewWidget
from orebiters_modding_tool.app.widgets.workspace import Workspace
from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.material import Material


def test_add_content_creates_item_updates_model_and_opens_editor(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Add content to the project and open its editor."""
    workspace.open_content(materials_category_reference)
    content_widget = workspace._get_content_widget(materials_category_reference)

    workspace._create_content(materials_category_reference, "iron_ore")

    project = workspace._project_service.active_project
    assert project is not None

    materials = project.content[ContentType.MATERIALS]
    assert len(materials) == 1
    assert isinstance(materials[0], Material)
    assert materials[0].id == "iron_ore"

    assert content_widget.model.rowCount() == 1
    assert content_widget.model.get_item(0) is materials[0]

    current_widget = workspace._tab_widget.currentWidget()
    assert isinstance(current_widget, BaseEditorWidget)
    assert current_widget.item is materials[0]


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

    workspace._delete_content(materials_category_reference, [material])

    assert project.content[ContentType.MATERIALS] == []
    assert content_widget.model.rowCount() == 0
    assert workspace._find_editor_tab(material) is None


def test_close_project_tabs_closes_project_tabs_and_keeps_welcome(
    workspace: Workspace,
    materials_category_reference: ContentReference,
) -> None:
    """Close project tabs without closing the Welcome tab."""
    workspace.open_content(materials_category_reference)
    workspace._create_content(materials_category_reference, "iron_ore")

    assert any(
        isinstance(
            workspace._tab_widget.widget(index),
            (ContentOverviewWidget, BaseEditorWidget),
        )
        for index in range(workspace._tab_widget.count())
    )

    workspace.close_project_tabs()

    assert workspace._tab_widget.count() == 1
    assert workspace._tab_widget.tabText(0) == "Welcome"
