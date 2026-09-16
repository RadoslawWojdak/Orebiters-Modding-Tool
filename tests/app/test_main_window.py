from unittest.mock import Mock, patch

from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication

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
