from unittest.mock import Mock, patch

from PySide6.QtGui import QCloseEvent, QKeySequence
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from orebiters_modding_tool.app.events.content import ContentChange, ContentChangeType
from orebiters_modding_tool.app.main_window import MainWindow
from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.services.project_service import ProjectService


def test_initializes_main_window(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Initialize the main window with its expected UI structure."""
    window = MainWindow(project_service)

    assert window.windowTitle() == "Orebiters Modding Tool"
    assert window.size().width() == MainWindow.DEFAULT_WIDTH
    assert window.size().height() == MainWindow.DEFAULT_HEIGHT
    assert window.centralWidget() is window._workspace
    assert window._project_explorer.parent() is window


def test_create_action_configures_action(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Create an action with its handler and shortcut."""
    window = MainWindow(project_service)
    handler = Mock()

    action = window._create_action("Test", handler, shortcut=QKeySequence.StandardKey.Save)

    assert action.text() == "Test"
    assert action.shortcut() == QKeySequence(QKeySequence.StandardKey.Save)

    action.trigger()

    handler.assert_called_once()


def test_open_content_shows_message_without_active_project(
    project_service: ProjectService,
    materials_category_reference: ContentReference,
    qapp: QApplication,
) -> None:
    """Show an error when opening content without an active project."""
    window = MainWindow(project_service)

    with patch("orebiters_modding_tool.app.main_window.QMessageBox.information") as information:
        window._open_content(materials_category_reference)

    information.assert_called_once_with(
        window,
        "No Project Open",
        "Please open or create a project before accessing content.",
    )


def test_open_content_delegates_to_workspace(
    project_service: ProjectService,
    materials_category_reference: ContentReference,
    qapp: QApplication,
) -> None:
    """Open content through the workspace when a project is active."""
    project_service.create_project("orebiters", "test")

    window = MainWindow(project_service)

    with patch.object(window._workspace, "open_content") as open_content:
        window._open_content(materials_category_reference)

    open_content.assert_called_once_with(materials_category_reference)


def test_set_active_project_updates_window(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Update the window after activating a project."""
    project = project_service.create_project("orebiters", "test")
    window = MainWindow(project_service)

    with (
        patch.object(window._workspace, "close_project_tabs") as close_tabs,
        patch.object(window, "_update_project_actions") as update_actions,
    ):
        window._set_active_project(project)

    assert window.windowTitle() == f"{project.name} - Orebiters Modding Tool"
    close_tabs.assert_called_once()
    update_actions.assert_called_once()


def test_save_project_saves_active_project(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Save the active project, refresh and show the current states."""
    project_service.create_project("orebiters", "test")
    project_service.mark_project_as_modified()
    window = MainWindow(project_service)

    with (
        patch.object(project_service, "save_project") as save_project,
        patch.object(window._workspace, "refresh_current_content_state") as refresh_state,
    ):
        window._save_project()

    save_project.assert_called_once()
    refresh_state.assert_called_once()
    assert window.statusBar().currentMessage() == "Project saved successfully"


def test_save_project_does_not_report_success_when_saving_fails(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Keep the project marked as unsaved when saving fails."""
    project_service.create_project("orebiters", "test")
    project_service.mark_project_as_modified()
    window = MainWindow(project_service)

    with (
        patch.object(project_service, "save_project", side_effect=OSError("Save failed")),
        patch("orebiters_modding_tool.app.main_window.QMessageBox.critical") as critical,
        patch.object(window._workspace, "refresh_current_content_state") as refresh_state,
    ):
        window._save_project()

    critical.assert_called_once_with(window, "Unable to Save Project", "Save failed")
    refresh_state.assert_not_called()
    assert window.statusBar().currentMessage() == ""
    assert window._project_status_label.text() == "Unsaved project changes"


def test_open_project_shows_message_when_no_projects_exist(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Show a message when no projects are available."""
    window = MainWindow(project_service)

    with patch("orebiters_modding_tool.app.main_window.QMessageBox.information") as information:
        window._open_action.trigger()

    information.assert_called_once_with(window, "Open Project", "No projects were found.")


def test_open_project_does_nothing_when_project_selection_is_cancelled(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Do nothing when project selection is canceled."""
    first_project = project_service.create_project("orebiters", "first")
    second_project = project_service.create_project("orebiters", "second")

    project_service.open_project(first_project.qualified_id)
    window = MainWindow(project_service)

    with patch(
        "orebiters_modding_tool.app.main_window.QInputDialog.getItem",
        return_value=(second_project.qualified_id, False),
    ):
        window._open_action.trigger()

    assert project_service.active_project is not None
    assert project_service.active_project.qualified_id == first_project.qualified_id


def test_open_project_opens_selected_project_without_unsaved_changes(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Open the selected project when the current project is saved."""
    first_project = project_service.create_project("orebiters", "first")
    second_project = project_service.create_project("orebiters", "second")

    project_service.open_project(first_project.qualified_id)
    window = MainWindow(project_service)

    with (
        patch(
            "orebiters_modding_tool.app.main_window.QInputDialog.getItem",
            return_value=(second_project.qualified_id, True),
        ),
        patch.object(window._workspace, "close_project_tabs") as close_tabs,
    ):
        window._open_action.trigger()

    assert project_service.active_project is not None
    assert project_service.active_project.qualified_id == second_project.qualified_id
    assert window.windowTitle() == f"{second_project.name} - Orebiters Modding Tool"
    assert window._project_status_label.text() == "All changes saved"
    close_tabs.assert_called_once()


@patch(
    "orebiters_modding_tool.app.main_window.QMessageBox.question",
    return_value=QMessageBox.StandardButton.Yes,
)
@patch("orebiters_modding_tool.app.main_window.QInputDialog.getItem")
def test_open_project_saves_unsaved_changes_before_opening_selected_project(
    get_item: Mock,
    question: Mock,
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Save unsaved changes before opening another project."""
    first_project = project_service.create_project("orebiters", "first")
    second_project = project_service.create_project("orebiters", "second")

    project_service.open_project(first_project.qualified_id)
    project_service.mark_project_as_modified()

    get_item.return_value = (second_project.qualified_id, True)

    window = MainWindow(project_service)

    with (
        patch.object(project_service, "save_project") as save_project,
        patch.object(window._workspace, "close_project_tabs") as close_tabs,
    ):
        window._open_action.trigger()

    question.assert_called_once()
    save_project.assert_called_once()
    close_tabs.assert_called_once()

    assert project_service.active_project is not None
    assert project_service.active_project.qualified_id == second_project.qualified_id
    assert window._project_status_label.text() == "All changes saved"


@patch(
    "orebiters_modding_tool.app.main_window.QMessageBox.question",
    return_value=QMessageBox.StandardButton.No,
)
@patch("orebiters_modding_tool.app.main_window.QInputDialog.getItem")
def test_open_project_discards_unsaved_changes_when_user_selects_no(
    get_item: Mock,
    _question: Mock,
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Discard unsaved changes and open the selected project."""
    first_project = project_service.create_project("orebiters", "first")
    second_project = project_service.create_project("orebiters", "second")

    project_service.open_project(first_project.qualified_id)
    project_service.mark_project_as_modified()

    get_item.return_value = (second_project.qualified_id, True)

    window = MainWindow(project_service)

    with patch.object(project_service, "save_project") as save_project:
        window._open_action.trigger()

    save_project.assert_not_called()

    assert project_service.active_project is not None
    assert project_service.active_project.qualified_id == second_project.qualified_id


@patch(
    "orebiters_modding_tool.app.main_window.QMessageBox.question",
    return_value=QMessageBox.StandardButton.Cancel,
)
@patch("orebiters_modding_tool.app.main_window.QInputDialog.getItem")
def test_open_project_cancels_when_user_selects_cancel_for_unsaved_changes(
    get_item: Mock,
    _question: Mock,
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Keep the current project open when the user cancels."""
    first_project = project_service.create_project("orebiters", "first")
    second_project = project_service.create_project("orebiters", "second")

    project_service.open_project(first_project.qualified_id)
    project_service.mark_project_as_modified()

    get_item.return_value = (second_project.qualified_id, True)

    window = MainWindow(project_service)

    with patch.object(project_service, "open_project") as open_project:
        window._open_action.trigger()

    open_project.assert_not_called()

    assert project_service.active_project is not None
    assert project_service.active_project.qualified_id == first_project.qualified_id


@patch(
    "orebiters_modding_tool.app.main_window.QMessageBox.question",
    return_value=QMessageBox.StandardButton.Yes,
)
@patch("orebiters_modding_tool.app.main_window.QInputDialog.getItem")
def test_open_project_stops_when_saving_unsaved_changes_fails(
    get_item: Mock,
    _question: Mock,
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Stop opening the project when saving unsaved changes fails."""
    first_project = project_service.create_project("orebiters", "first")
    second_project = project_service.create_project("orebiters", "second")

    project_service.open_project(first_project.qualified_id)
    project_service.mark_project_as_modified()

    get_item.return_value = (second_project.qualified_id, True)

    window = MainWindow(project_service)

    with (
        patch.object(
            project_service, "save_project", side_effect=OSError("Save failed")
        ) as save_project,
        patch("orebiters_modding_tool.app.main_window.QMessageBox.critical") as critical,
        patch.object(project_service, "open_project") as open_project,
    ):
        window._open_action.trigger()

    save_project.assert_called_once()
    open_project.assert_not_called()
    critical.assert_called_once()

    assert project_service.active_project is not None
    assert project_service.active_project.qualified_id == first_project.qualified_id
    assert window._project_status_label.text() == "Unsaved project changes"


@patch("orebiters_modding_tool.app.main_window.QInputDialog.getItem")
def test_open_project_shows_error_when_opening_project_fails(
    get_item: Mock,
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Show an error when the selected project cannot be opened."""
    first_project = project_service.create_project("orebiters", "first")
    second_project = project_service.create_project("orebiters", "second")

    project_service.open_project(first_project.qualified_id)
    get_item.return_value = (second_project.qualified_id, True)

    window = MainWindow(project_service)

    with (
        patch.object(
            project_service, "open_project", side_effect=OSError("Open failed")
        ) as open_project,
        patch("orebiters_modding_tool.app.main_window.QMessageBox.critical") as critical,
    ):
        window._open_action.trigger()

    open_project.assert_called_once_with(second_project.qualified_id)

    critical.assert_called_once_with(window, "Unable to Open Project", "Open failed")

    assert project_service.active_project is not None
    assert project_service.active_project.qualified_id == first_project.qualified_id


def test_update_project_actions_enables_save_for_active_project(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Enable project-dependent actions when a project is active."""
    project_service.create_project("orebiters", "test")
    window = MainWindow(project_service)

    window._update_project_actions()

    assert window._save_action.isEnabled()


def test_update_project_actions_disables_save_without_active_project(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Disable project-dependent actions when no project is active."""
    window = MainWindow(project_service)

    window._update_project_actions()

    assert not window._save_action.isEnabled()


@patch(
    "orebiters_modding_tool.app.main_window.QMessageBox.question",
    return_value=QMessageBox.StandardButton.Yes,
)
@patch("orebiters_modding_tool.app.main_window.NewProjectDialog")
def test_new_project_saves_changes_before_creating_project(
    new_project_dialog: Mock,
    _question: Mock,
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Save unsaved changes before creating a new project."""
    project_service.create_project("orebiters", "existing")
    project_service.mark_project_as_modified()

    dialog = new_project_dialog.return_value
    dialog.exec.return_value = QDialog.DialogCode.Accepted
    dialog.namespace = "orebiters"
    dialog.name = "new"

    window = MainWindow(project_service)

    with patch.object(project_service, "save_project") as save_project:
        window._new_action.trigger()

    save_project.assert_called_once()

    assert project_service.active_project is not None
    assert project_service.active_project.name == "new"
    assert window._project_status_label.text() == "All changes saved"


@patch(
    "orebiters_modding_tool.app.main_window.QMessageBox.question",
    return_value=QMessageBox.StandardButton.No,
)
@patch("orebiters_modding_tool.app.main_window.NewProjectDialog")
def test_new_project_discards_changes_and_creates_project(
    new_project_dialog: Mock,
    _question: Mock,
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Discard unsaved changes and create a new project."""
    project_service.create_project("orebiters", "existing")
    project_service.mark_project_as_modified()

    dialog = new_project_dialog.return_value
    dialog.exec.return_value = QDialog.DialogCode.Accepted
    dialog.namespace = "orebiters"
    dialog.name = "new"

    window = MainWindow(project_service)

    with patch.object(project_service, "save_project") as save_project:
        window._new_action.trigger()

    save_project.assert_not_called()

    assert project_service.active_project is not None
    assert project_service.active_project.name == "new"


@patch(
    "orebiters_modding_tool.app.main_window.QMessageBox.question",
    return_value=QMessageBox.StandardButton.Cancel,
)
@patch("orebiters_modding_tool.app.main_window.NewProjectDialog")
def test_new_project_cancels_when_user_cancels_unsaved_changes(
    new_project_dialog: Mock,
    _question: Mock,
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Keep the current project when unsaved changes are canceled."""
    existing_project = project_service.create_project("orebiters", "existing")
    project_service.mark_project_as_modified()

    dialog = new_project_dialog.return_value
    dialog.exec.return_value = QDialog.DialogCode.Accepted
    dialog.namespace = "orebiters"
    dialog.name = "new"

    window = MainWindow(project_service)

    with patch.object(project_service, "create_project") as create_project:
        window._new_action.trigger()

    create_project.assert_not_called()

    assert project_service.active_project is not None
    assert project_service.active_project.qualified_id == existing_project.qualified_id


@patch(
    "orebiters_modding_tool.app.main_window.QMessageBox.question",
    return_value=QMessageBox.StandardButton.Yes,
)
def test_close_event_saves_changes_and_accepts_event(
    _question: Mock,
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Save unsaved changes and accept the close event."""
    project_service.create_project("orebiters", "test")
    project_service.mark_project_as_modified()

    window = MainWindow(project_service)
    event = QCloseEvent()

    with patch.object(project_service, "save_project") as save_project:
        window.closeEvent(event)

    save_project.assert_called_once()
    assert event.isAccepted()


@patch(
    "orebiters_modding_tool.app.main_window.QMessageBox.question",
    return_value=QMessageBox.StandardButton.No,
)
def test_close_event_discards_changes_and_accepts_event(
    _question: Mock,
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Discard unsaved changes and accept the close event."""
    project_service.create_project("orebiters", "test")
    project_service.mark_project_as_modified()

    window = MainWindow(project_service)
    event = QCloseEvent()

    with patch.object(project_service, "save_project") as save_project:
        window.closeEvent(event)

    save_project.assert_not_called()
    assert event.isAccepted()


@patch(
    "orebiters_modding_tool.app.main_window.QMessageBox.question",
    return_value=QMessageBox.StandardButton.Cancel,
)
def test_close_event_ignores_event_when_user_cancels(
    _question: Mock,
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Ignore the close event when the user cancels."""
    project_service.create_project("orebiters", "test")
    project_service.mark_project_as_modified()

    window = MainWindow(project_service)
    event = QCloseEvent()

    with patch.object(project_service, "save_project") as save_project:
        window.closeEvent(event)

    save_project.assert_not_called()
    assert not event.isAccepted()


# =============================================================================
# Status Bar
# =============================================================================


def test_initializes_status_bar(project_service: ProjectService, qapp: QApplication) -> None:
    """Initialize the status bar with project status and statistics."""
    window = MainWindow(project_service)

    assert window.statusBar() is window._status_bar
    assert window._project_status_label.text() == "No project open"
    assert window._project_statistics_label.text() == ""


def test_project_status_reflects_save_state(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Show the current saved state of the active project."""
    project_service.create_project("orebiters", "test")
    window = MainWindow(project_service)

    assert window._project_status_label.text() == "All changes saved"

    project_service.mark_project_as_modified()
    window._refresh_status_bar()

    assert window._project_status_label.text() == "Unsaved project changes"

    window._save_project()

    assert window._project_status_label.text() == "All changes saved"


def test_project_statistics_reflect_active_project_content(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Display content counts for the active project."""
    project = project_service.create_project("orebiters", "test")
    window = MainWindow(project_service)

    expected_statistics = " | ".join(
        f"{content_type.display_name}: {len(project.content[content_type])}"
        for content_type in ContentType
    )

    assert window._project_statistics_label.text() == expected_statistics


def test_status_message_is_displayed(project_service: ProjectService, qapp: QApplication) -> None:
    """Display a temporary message in the status bar."""
    window = MainWindow(project_service)

    window._show_status_message("Test message")

    assert window.statusBar().currentMessage() == "Test message"


def test_formats_created_content_change(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Format a created content change for the status bar."""
    window = MainWindow(project_service)
    change = ContentChange(
        change_type=ContentChangeType.CREATED,
        content_type=ContentType.MATERIALS,
        content_name="orebiters.test.materials.iron_ore",
    )

    assert window._format_content_change(change) == "Created orebiters.test.materials.iron_ore"


def test_formats_updated_content_change(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Format an updated content change for the status bar."""
    window = MainWindow(project_service)
    change = ContentChange(
        change_type=ContentChangeType.UPDATED,
        content_type=ContentType.MATERIALS,
        content_name="orebiters.test.materials.iron_ore",
    )

    assert window._format_content_change(change) == "Updated orebiters.test.materials.iron_ore"


def test_formats_removed_single_content_change(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Use the singular content name when one item is removed."""
    window = MainWindow(project_service)
    change = ContentChange(
        change_type=ContentChangeType.REMOVED,
        content_type=ContentType.MATERIALS,
        count=1,
    )

    expected = f"Removed 1 {ContentType.MATERIALS.singular_display_name.lower()}"

    assert window._format_content_change(change) == expected


def test_formats_removed_multiple_content_change(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Use the plural content name when multiple items are removed."""
    window = MainWindow(project_service)
    change = ContentChange(
        change_type=ContentChangeType.REMOVED,
        content_type=ContentType.MATERIALS,
        count=2,
    )

    expected = f"Removed 2 {ContentType.MATERIALS.display_name.lower()}"

    assert window._format_content_change(change) == expected


def test_formats_unknown_content_change(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Use a fallback message for an unsupported content change type."""
    window = MainWindow(project_service)
    change = ContentChange(
        change_type=Mock(),
        content_type=ContentType.MATERIALS,
    )

    assert window._format_content_change(change) == "Content changed"


def test_workspace_content_changed_updates_visible_ui(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Reflect a content change in the status bar."""
    window = MainWindow(project_service)
    change = ContentChange(
        change_type=ContentChangeType.CREATED,
        content_type=ContentType.MATERIALS,
        content_name="orebiters.test.materials.iron_ore",
    )

    window._on_workspace_content_changed(change)

    assert window.statusBar().currentMessage() == "Created orebiters.test.materials.iron_ore"


def test_save_project_displays_success_message(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Display a success message after saving the project."""
    project_service.create_project("orebiters", "test")
    window = MainWindow(project_service)

    window._save_project()

    assert window.statusBar().currentMessage() == "Project saved successfully"


def test_new_project_displays_success_message(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Display a success message after creating a project."""
    with patch("orebiters_modding_tool.app.main_window.NewProjectDialog") as new_project_dialog:
        dialog = new_project_dialog.return_value
        dialog.exec.return_value = QDialog.DialogCode.Accepted
        dialog.namespace = "orebiters"
        dialog.name = "test"

        window = MainWindow(project_service)
        window._new_project()

    assert window.statusBar().currentMessage() == "Project created successfully"


def test_refresh_projects_displays_success_message(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Display a success message after refreshing projects."""
    window = MainWindow(project_service)

    window._refresh_projects()

    assert window.statusBar().currentMessage() == "Projects refreshed successfully"


def test_refresh_projects_does_not_display_success_message_on_failure(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Do not display a success message when refreshing projects fails."""
    window = MainWindow(project_service)

    with (
        patch.object(project_service, "refresh_projects", side_effect=OSError("Refresh failed")),
        patch("orebiters_modding_tool.app.main_window.QMessageBox.critical"),
    ):
        window._refresh_projects()

    assert window.statusBar().currentMessage() == ""
