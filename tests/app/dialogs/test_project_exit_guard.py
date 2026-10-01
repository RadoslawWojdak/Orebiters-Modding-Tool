from unittest.mock import patch

from PySide6.QtWidgets import QMessageBox, QWidget
from pytestqt.qtbot import QtBot

from orebiters_modding_tool.app.dialogs.project_exit_guard import ProjectExitGuard
from orebiters_modding_tool.app.widgets.workspace import Workspace


def create_guard(workspace: Workspace, qtbot: QtBot) -> tuple[ProjectExitGuard, QWidget]:
    """Create a guard and its Qt parent managed by pytest-qt."""
    parent = QWidget()
    qtbot.addWidget(parent)

    return ProjectExitGuard(workspace._project_service, workspace, parent), parent


def test_allows_exit_when_project_has_no_unsaved_changes(
    workspace: Workspace,
    qtbot: QtBot,
) -> None:
    """Allow exit without asking to save when the project is unchanged."""
    guard, _parent = create_guard(workspace, qtbot)

    with patch.object(QMessageBox, "question") as question:
        result = guard.confirm_unsaved_project_exit()

    assert result is True
    question.assert_not_called()


def test_saves_changes_when_user_confirms(workspace: Workspace, qtbot: QtBot) -> None:
    """Save project changes and allow exit when the user selects Yes."""
    project_service = workspace._project_service
    project_service.mark_project_as_modified()
    guard, parent = create_guard(workspace, qtbot)

    with (
        patch.object(
            QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes
        ) as question,
        patch.object(
            project_service, "save_project", wraps=project_service.save_project
        ) as save_project,
    ):
        result = guard.confirm_unsaved_project_exit()

    assert result is True
    question.assert_called_once_with(
        parent,
        "Unsaved Changes",
        "The current project has unsaved changes.\n"
        "Do you want to save your changes before continuing?",
        (
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel
        ),
        QMessageBox.StandardButton.Yes,
    )
    save_project.assert_called_once_with()
    assert project_service.has_unsaved_changes is False


def test_allows_exit_without_saving_when_user_selects_no(
    workspace: Workspace,
    qtbot: QtBot,
) -> None:
    """Allow exit without saving when the user selects No."""
    project_service = workspace._project_service
    project_service.mark_project_as_modified()
    guard, _parent = create_guard(workspace, qtbot)

    with (
        patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.No),
        patch.object(project_service, "save_project") as save_project,
    ):
        result = guard.confirm_unsaved_project_exit()

    assert result is True
    save_project.assert_not_called()
    assert project_service.has_unsaved_changes is True


def test_cancels_exit_when_user_selects_cancel(workspace: Workspace, qtbot: QtBot) -> None:
    """Cancel the exit operation when the user selects Cancel."""
    project_service = workspace._project_service
    project_service.mark_project_as_modified()
    guard, _parent = create_guard(workspace, qtbot)

    with (
        patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel),
        patch.object(project_service, "save_project") as save_project,
    ):
        result = guard.confirm_unsaved_project_exit()

    assert result is False
    save_project.assert_not_called()
    assert project_service.has_unsaved_changes is True


def test_cancels_exit_and_shows_error_when_saving_fails(workspace: Workspace, qtbot: QtBot) -> None:
    """Cancel exit and display an error when saving raises an exception."""
    project_service = workspace._project_service
    project_service.mark_project_as_modified()
    guard, parent = create_guard(workspace, qtbot)

    with (
        patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes),
        patch.object(
            project_service, "save_project", side_effect=OSError("Save failed")
        ) as save_project,
        patch.object(QMessageBox, "critical") as critical,
    ):
        result = guard.confirm_unsaved_project_exit()

    assert result is False
    save_project.assert_called_once_with()
    critical.assert_called_once_with(
        parent,
        "Save Failed",
        "The project could not be saved. The operation has been cancelled.",
    )
    assert project_service.has_unsaved_changes is True


def test_cancels_exit_when_project_tabs_cannot_be_closed(
    workspace: Workspace,
    qtbot: QtBot,
) -> None:
    """Cancel exit before asking about project changes when tabs cannot close."""
    project_service = workspace._project_service
    project_service.mark_project_as_modified()
    guard, _parent = create_guard(workspace, qtbot)

    with (
        patch.object(workspace, "confirm_project_tabs_close", return_value=False) as confirm_tabs,
        patch.object(QMessageBox, "question") as question,
        patch.object(project_service, "save_project") as save_project,
    ):
        result = guard.confirm_unsaved_project_exit()

    assert result is False
    confirm_tabs.assert_called_once_with()
    question.assert_not_called()
    save_project.assert_not_called()
    assert project_service.has_unsaved_changes is True
