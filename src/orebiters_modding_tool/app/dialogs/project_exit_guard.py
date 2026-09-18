from PySide6.QtWidgets import QMessageBox, QWidget

from orebiters_modding_tool.services.project_service import ProjectService


class ProjectExitGuard:
    """Protect the active project from accidental loss of changes."""

    def __init__(self, project_service: ProjectService, parent: QWidget) -> None:
        """Initialize the project exit guard.

        :param project_service: Service managing the active project.
        :param parent: Parent widget for confirmation dialogs.
        """
        self._project_service = project_service
        self._parent = parent

    def confirm_unsaved_project_exit(self) -> bool:
        """Ask whether the active unsaved project can be closed.

        :returns: True if the project can be safely closed.
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
