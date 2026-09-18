from unittest.mock import Mock, patch

from PySide6.QtGui import QCloseEvent, QKeySequence
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from orebiters_modding_tool.app.main_window import MainWindow
from orebiters_modding_tool.domain.content import ContentReference
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
    """Save the active project and refresh the current content state."""
    project_service.create_project("orebiters", "test")
    window = MainWindow(project_service)

    with (
        patch.object(project_service, "save_project") as save_project,
        patch.object(window._workspace, "refresh_current_content_state") as refresh_state,
    ):
        window._save_project()

    save_project.assert_called_once()
    refresh_state.assert_called_once()


def test_save_project_does_not_refresh_content_state_on_failure(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Do not refresh the content state when saving the project fails."""
    project_service.create_project("orebiters", "test")
    window = MainWindow(project_service)

    with (
        patch.object(project_service, "save_project", side_effect=OSError("Save failed")),
        patch("orebiters_modding_tool.app.main_window.QMessageBox.critical") as critical,
        patch.object(window._workspace, "refresh_current_content_state") as refresh_state,
    ):
        window._save_project()

    critical.assert_called_once_with(window, "Unable to Save Project", "Save failed")
    refresh_state.assert_not_called()


def test_save_project_shows_error_on_failure(
    project_service: ProjectService,
    qapp: QApplication,
) -> None:
    """Show an error when saving the project fails."""
    project_service.create_project("orebiters", "test")
    window = MainWindow(project_service)

    with (
        patch.object(project_service, "save_project", side_effect=OSError("Save failed")),
        patch("orebiters_modding_tool.app.main_window.QMessageBox.critical") as critical,
    ):
        window._save_project()

    critical.assert_called_once_with(window, "Unable to Save Project", "Save failed")


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
    assert window.windowTitle() == (f"{second_project.name} - Orebiters Modding Tool")
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

    assert project_service.active_project is not None
    assert project_service.active_project.qualified_id == second_project.qualified_id
    close_tabs.assert_called_once()


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
    dialog.exec.return_value = 1
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
