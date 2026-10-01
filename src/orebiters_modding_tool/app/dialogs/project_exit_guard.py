from PySide6.QtWidgets import QMessageBox, QWidget

from orebiters_modding_tool.app.widgets.workspace import Workspace
from orebiters_modding_tool.services.project_service import ProjectService


class ProjectExitGuard:
    """Protect the active project from accidental loss of changes."""

    def __init__(
        self,
        project_service: ProjectService,
        workspace: Workspace,
        parent: QWidget,
    ) -> None:
        """Initialize the project exit guard.

        :param project_service: Service managing the active project.
        :param workspace: Workspace managing project tabs and editors.
        :param parent: Parent widget for confirmation dialogs.
        """
        self._project_service = project_service
        self._workspace = workspace
        self._parent = parent

    def confirm_unsaved_project_exit(self) -> bool:
        """Confirm that the active project can be safely closed.

        :returns: True if the project can be closed.
        """
        if not self._workspace.confirm_project_tabs_close():
            return False

        return self._confirm_project_changes()

    def _confirm_project_changes(self) -> bool:
        """Confirm handling unsaved project changes.

        :returns: True if the project can be closed.
        """
        if not self._project_service.has_unsaved_changes:
            return True

        result = QMessageBox.question(
            self._parent,
            "Unsaved Changes",
            "The current project has unsaved changes.\n"
            "Do you want to save your changes before continuing?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes,
        )

        if result == QMessageBox.StandardButton.Yes:
            try:
                self._project_service.save_project()
            except Exception:
                QMessageBox.critical(
                    self._parent,
                    "Save Failed",
                    "The project could not be saved. The operation has been cancelled.",
                )
                return False

            return True

        return result == QMessageBox.StandardButton.No
