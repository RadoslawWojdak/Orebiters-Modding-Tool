from unittest.mock import patch

from PySide6.QtWidgets import QMessageBox, QWidget

from orebiters_modding_tool.app.dialogs.project_exit_guard import ProjectExitGuard
from orebiters_modding_tool.services.project_service import ProjectService


def test_returns_true_without_unsaved_changes(project_service: ProjectService, qapp) -> None:
    """Allow project exit when there are no unsaved changes."""
    guard = ProjectExitGuard(project_service, QWidget())

    assert guard.confirm_unsaved_project_exit() is True


@patch(
    "orebiters_modding_tool.app.dialogs.project_exit_guard.QMessageBox.question",
    return_value=QMessageBox.StandardButton.Yes,
)
def test_saves_changes_and_confirms_exit(
    _mock_question,
    active_project_service: ProjectService,
    qapp,
) -> None:
    """Save changes and allow project exit."""
    active_project_service.mark_project_as_modified()

    guard = ProjectExitGuard(active_project_service, QWidget())

    assert guard.confirm_unsaved_project_exit() is True
    assert active_project_service.has_unsaved_changes is False


@patch(
    "orebiters_modding_tool.app.dialogs.project_exit_guard.QMessageBox.question",
    return_value=QMessageBox.StandardButton.No,
)
def test_discards_changes_and_confirms_exit(
    _mock_question,
    active_project_service: ProjectService,
    qapp,
) -> None:
    """Discard changes and allow project exit."""
    active_project_service.mark_project_as_modified()

    guard = ProjectExitGuard(active_project_service, QWidget())

    assert guard.confirm_unsaved_project_exit() is True
    assert active_project_service.has_unsaved_changes is True


@patch(
    "orebiters_modding_tool.app.dialogs.project_exit_guard.QMessageBox.question",
    return_value=QMessageBox.StandardButton.Cancel,
)
def test_cancel_prevents_project_exit(
    _mock_question,
    active_project_service: ProjectService,
    qapp,
) -> None:
    """Keep the project open when exit is cancelled."""
    active_project_service.mark_project_as_modified()

    guard = ProjectExitGuard(active_project_service, QWidget())

    assert guard.confirm_unsaved_project_exit() is False
    assert active_project_service.has_unsaved_changes is True


@patch("orebiters_modding_tool.app.dialogs.project_exit_guard.QMessageBox.critical")
@patch(
    "orebiters_modding_tool.app.dialogs.project_exit_guard.QMessageBox.question",
    return_value=QMessageBox.StandardButton.Yes,
)
def test_save_failure_prevents_project_exit(
    _mock_question,
    mock_critical,
    active_project_service: ProjectService,
) -> None:
    """Prevent project exit when saving fails."""
    active_project_service.mark_project_as_modified()

    guard = ProjectExitGuard(active_project_service, QWidget())

    with patch.object(active_project_service, "save_project", side_effect=OSError("Save failed")):
        assert guard.confirm_unsaved_project_exit() is False

    assert active_project_service.has_unsaved_changes is True
    mock_critical.assert_called_once()
