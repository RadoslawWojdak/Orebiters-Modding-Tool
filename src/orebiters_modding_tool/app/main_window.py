import json
from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QStyle,
    QToolBar,
)

from orebiters_modding_tool.app.dialogs.new_project_dialog import NewProjectDialog
from orebiters_modding_tool.app.dialogs.project_exit_guard import ProjectExitGuard
from orebiters_modding_tool.app.docks.project_explorer import ProjectExplorer
from orebiters_modding_tool.app.events.content import ContentChange, ContentChangeType
from orebiters_modding_tool.app.widgets.workspace import Workspace
from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.services.project_service import ProjectService


class MainWindow(QMainWindow):
    """Main window of the application."""

    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 600

    def __init__(self, project_service: ProjectService) -> None:
        """Initialize the main window.

        :param project_service: Service used to manage mod projects.
        """
        super().__init__()

        self._project_service = project_service
        self._project_exit_guard = ProjectExitGuard(self._project_service, self)

        self.setWindowTitle("Orebiters Modding Tool")
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

        self._setup_actions()
        self._setup_project_explorer()
        self._setup_workspace()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_status_bar()

        self._update_project_actions()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle the main window close request.

        :param event: Window close event.
        """
        if self._project_exit_guard.confirm_unsaved_project_exit():
            event.accept()
        else:
            event.ignore()

    def _setup_workspace(self) -> None:
        """Set up the central application workspace."""
        self._workspace = Workspace(self._project_service, self)
        self._workspace.content_changed.connect(self._on_workspace_content_changed)

        self.setCentralWidget(self._workspace)

    def _setup_actions(self) -> None:
        """Set up the application actions."""
        style = self.style()

        # File Actions
        self._new_action = self._create_action(
            "New",
            self._new_project,
            shortcut=QKeySequence.StandardKey.New,
            icon=style.standardIcon(QStyle.StandardPixmap.SP_FileIcon),
        )
        self._open_action = self._create_action(
            "Open",
            self._open_project,
            shortcut=QKeySequence.StandardKey.Open,
            icon=style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton),
        )
        self._save_action = self._create_action(
            "Save",
            self._save_project,
            shortcut=QKeySequence.StandardKey.Save,
            icon=style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton),
        )
        self._refresh_projects_action = self._create_action(
            "Refresh Projects",
            self._refresh_projects,
            icon=style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload),
        )
        self._exit_action = self._create_action(
            "Exit",
            self._exit_application,
            shortcut=QKeySequence.StandardKey.Quit,
            icon=style.standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton),
        )

        # Edit Actions
        self._undo_action = self._create_action(
            "Undo",
            self._undo,
            shortcut=QKeySequence.StandardKey.Undo,
            icon=style.standardIcon(QStyle.StandardPixmap.SP_ArrowBack),
        )
        self._undo_action.setEnabled(False)
        self._redo_action = self._create_action(
            "Redo",
            self._redo,
            shortcut=QKeySequence.StandardKey.Redo,
            icon=style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward),
        )
        self._redo_action.setEnabled(False)
        self._cut_action = self._create_action(
            "Cut",
            self._cut,
            shortcut=QKeySequence.StandardKey.Cut,
        )
        self._cut_action.setEnabled(False)
        self._copy_action = self._create_action(
            "Copy",
            self._copy,
            shortcut=QKeySequence.StandardKey.Copy,
        )
        self._copy_action.setEnabled(False)
        self._paste_action = self._create_action(
            "Paste",
            self._paste,
            shortcut=QKeySequence.StandardKey.Paste,
        )
        self._paste_action.setEnabled(False)

        # Help Actions
        self._show_documentation_action = self._create_action(
            "Documentation",
            self._show_documentation,
            shortcut=QKeySequence.StandardKey.HelpContents,
            icon=style.standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton),
        )
        self._show_documentation_action.setEnabled(False)
        self._show_keyboard_shortcuts_action = self._create_action(
            "Keyboard Shortcuts",
            self._show_keyboard_shortcuts,
        )
        self._show_keyboard_shortcuts_action.setEnabled(False)
        self._show_about_dialog_action = self._create_action(
            "About",
            self._show_about_dialog,
            icon=style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation),
        )
        self._show_about_dialog_action.setEnabled(False)

    def _setup_menu_bar(self) -> None:
        """Set up the application menu bar."""
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self._new_action)
        file_menu.addAction(self._open_action)
        file_menu.addAction(self._save_action)
        file_menu.addSeparator()
        file_menu.addAction(self._refresh_projects_action)
        file_menu.addSeparator()
        file_menu.addAction(self._exit_action)

        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction(self._undo_action)
        edit_menu.addAction(self._redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self._cut_action)
        edit_menu.addAction(self._copy_action)
        edit_menu.addAction(self._paste_action)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self._show_documentation_action)
        help_menu.addAction(self._show_keyboard_shortcuts_action)
        help_menu.addSeparator()
        help_menu.addAction(self._show_about_dialog_action)

    def _setup_status_bar(self) -> None:
        """Set up the application status bar."""
        self._status_bar = QStatusBar(self)
        self.setStatusBar(self._status_bar)

        self._project_status_label = QLabel(self)
        self._project_statistics_label = QLabel(self)

        self._project_status_label.setContentsMargins(6, 0, 6, 0)

        self._status_bar.addWidget(self._project_status_label)
        self._status_bar.addPermanentWidget(self._project_statistics_label)

        self._refresh_status_bar()

    def _setup_toolbar(self) -> None:
        """Set up the application toolbar."""
        toolbar = QToolBar("Main Toolbar", self)
        self.addToolBar(toolbar)

        toolbar.addAction(self._new_action)
        toolbar.addAction(self._open_action)
        toolbar.addAction(self._save_action)

    def _setup_project_explorer(self) -> None:
        """Set up the Project Explorer dock."""
        self._project_explorer = ProjectExplorer(self._project_service, self)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._project_explorer)

        self._project_explorer.content_open_requested.connect(self._open_content)

    def _on_workspace_content_changed(self, change: ContentChange) -> None:
        """Handle content changes reported by the workspace."""
        self._project_explorer.refresh()
        self._refresh_status_bar()
        self._show_status_message(self._format_content_change(change))

    def _create_action(
        self,
        text: str,
        handler: Callable[[], None],
        *,
        shortcut: QKeySequence.StandardKey | str | None = None,
        icon: QIcon | None = None,
    ) -> QAction:
        """Create and configure an application action.

        :param text: Text displayed for the action.
        :param handler: Callback executed when the action is triggered.
        :param shortcut: Optional keyboard shortcut.
        :param icon: Optional action icon.
        :returns: Configured application action.
        """
        action = QAction(icon, text, self) if icon is not None else QAction(text, self)

        if shortcut is not None:
            action.setShortcut(shortcut)

        action.triggered.connect(handler)

        return action

    def _new_project(self) -> None:
        """Create a new project."""
        dialog = NewProjectDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        if not self._project_exit_guard.confirm_unsaved_project_exit():
            return

        try:
            project = self._project_service.create_project(dialog.namespace, dialog.name)
        except FileExistsError:
            QMessageBox.warning(
                self,
                "Project Already Exists",
                "A project with this identifier already exists.",
            )
            return

        self._set_active_project(project)

        self._refresh_status_bar()
        self._show_status_message("Project created successfully")

    def _open_project(self) -> None:
        """Open an existing project."""
        project_ids = self._project_service.list_project_qualified_ids()

        if not project_ids:
            QMessageBox.information(self, "Open Project", "No projects were found.")
            return

        qualified_id, accepted = QInputDialog.getItem(
            self,
            "Open Project",
            "Project:",
            project_ids,
            editable=False,
        )

        if not accepted:
            return

        if not self._project_exit_guard.confirm_unsaved_project_exit():
            return

        try:
            project = self._project_service.open_project(qualified_id)
        except (
            FileNotFoundError,
            PermissionError,
            OSError,
            ValueError,
            KeyError,
            json.JSONDecodeError,
        ) as error:
            QMessageBox.critical(self, "Unable to Open Project", str(error))
            return

        self._set_active_project(project)

        self._refresh_status_bar()
        self._show_status_message("Project opened successfully")

    def _save_project(self) -> None:
        """Save the current project."""
        try:
            self._project_service.save_project()
        except OSError as error:
            QMessageBox.critical(self, "Unable to Save Project", str(error))
            return

        self._workspace.refresh_current_content_state()

        self._refresh_status_bar()
        self._show_status_message("Project saved successfully")

    def _refresh_projects(self) -> None:
        """Refresh projects from persistent storage."""
        try:
            self._project_service.refresh_projects()
        except (
            FileNotFoundError,
            PermissionError,
            OSError,
            ValueError,
            KeyError,
            json.JSONDecodeError,
        ) as error:
            QMessageBox.critical(self, "Unable to Refresh Projects", str(error))
            return

        self._project_explorer.refresh()

        self._refresh_status_bar()
        self._show_status_message("Projects refreshed successfully")

    def _show_status_message(self, message: str) -> None:
        """Show a temporary status message."""
        self._status_bar.showMessage(message, 3000)

    def _refresh_status_bar(self) -> None:
        """Refresh the status bar."""
        self._update_project_status()
        self._update_project_statistics()

    def _exit_application(self) -> None:
        """Close the application."""
        self.close()

    def _undo(self) -> None:
        """Undo the previous action."""
        pass

    def _redo(self) -> None:
        """Redo the previously undone action."""
        pass

    def _cut(self) -> None:
        """Cut the selected content."""
        pass

    def _copy(self) -> None:
        """Copy the selected content."""
        pass

    def _paste(self) -> None:
        """Paste content from the clipboard."""
        pass

    def _show_documentation(self) -> None:
        """Show the application documentation."""
        pass

    def _show_keyboard_shortcuts(self) -> None:
        """Show the available keyboard shortcuts."""
        pass

    def _show_about_dialog(self) -> None:
        """Show information about the application."""
        pass

    def _open_content(self, content_reference: ContentReference) -> None:
        """Open the selected content in the workspace.

        :param content_reference: Reference to the selected content.
        """
        if not self._project_service.has_active_project:
            QMessageBox.information(
                self,
                "No Project Open",
                "Please open or create a project before accessing content.",
            )
            return

        self._workspace.open_content(content_reference)

    def _set_active_project(self, project: Project) -> None:
        """Update the window for the active project.

        :param project: Project that became active.
        """
        self.setWindowTitle(f"{project.name} - Orebiters Modding Tool")
        self._workspace.close_project_tabs()
        self._project_explorer.refresh()
        self._update_project_actions()

    def _update_project_actions(self) -> None:
        """Update actions that depend on an active project."""
        has_active_project = self._project_service.has_active_project

        self._save_action.setEnabled(has_active_project)

    def _update_project_status(self) -> None:
        """Update the active project save status."""
        if not self._project_service.has_active_project:
            self._project_status_label.setText("No project open")
            return

        if self._project_service.has_unsaved_changes:
            self._project_status_label.setText("Unsaved project changes")
            return

        self._project_status_label.setText("All changes saved")

    def _update_project_statistics(self) -> None:
        """Update the active project content statistics."""
        project = self._project_service.active_project

        if project is None:
            self._project_statistics_label.clear()
            return

        statistics = [
            f"{content_type.display_name}: {len(project.content[content_type])}"
            for content_type in ContentType
        ]

        self._project_statistics_label.setText(" | ".join(statistics))

    def _format_content_change(self, change: ContentChange) -> str:
        """Format a content change for the status bar."""
        if change.change_type is ContentChangeType.CREATED:
            return f"Created {change.content_name}"

        if change.change_type is ContentChangeType.UPDATED:
            return f"Updated {change.content_name}"

        if change.change_type is ContentChangeType.REMOVED:
            content_type_name = (
                change.content_type.singular_display_name
                if change.count == 1
                else change.content_type.display_name
            )
            return f"Removed {change.count} {content_type_name.lower()}"

        return "Content changed"
