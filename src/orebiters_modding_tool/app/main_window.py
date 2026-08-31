from collections.abc import Callable

from PySide6.QtGui import QAction, QIcon, QKeySequence, Qt
from PySide6.QtWidgets import QMainWindow, QStyle, QToolBar, QVBoxLayout, QWidget

from orebiters_modding_tool.app.docks.project_explorer import ProjectExplorer


class MainWindow(QMainWindow):
    """Main window of the application."""

    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 600

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Orebiters Modding Tool")
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

        self._setup_actions()
        self._setup_central_widget()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_project_explorer()

    def _setup_central_widget(self) -> None:
        """Set up the central application widget."""
        central_widget = QWidget()
        self._main_layout = QVBoxLayout(central_widget)

        self.setCentralWidget(central_widget)

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
        self._save_as_action = self._create_action(
            "Save As",
            self._save_project_as,
            shortcut=QKeySequence.StandardKey.SaveAs,
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
        self._redo_action = self._create_action(
            "Redo",
            self._redo,
            shortcut=QKeySequence.StandardKey.Redo,
            icon=style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward),
        )
        self._cut_action = self._create_action(
            "Cut",
            self._cut,
            shortcut=QKeySequence.StandardKey.Cut,
        )
        self._copy_action = self._create_action(
            "Copy",
            self._copy,
            shortcut=QKeySequence.StandardKey.Copy,
        )
        self._paste_action = self._create_action(
            "Paste",
            self._paste,
            shortcut=QKeySequence.StandardKey.Paste,
        )
        self._add_content_action = self._create_action(
            "Add Content",
            self._add_content,
            shortcut="Ctrl+Shift+N",
            icon=QIcon(":/icons/add.svg"),
        )
        self._delete_selected_content_action = self._create_action(
            "Delete Selected Content",
            self._delete_selected_content,
            shortcut=QKeySequence.StandardKey.Delete,
            icon=style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon),
        )
        self._select_all_content_action = self._create_action(
            "Select All Content",
            self._select_all_content,
            shortcut=QKeySequence.StandardKey.SelectAll,
        )

        # Help Actions
        self._show_documentation_action = self._create_action(
            "Documentation",
            self._show_documentation,
            shortcut=QKeySequence.StandardKey.HelpContents,
            icon=style.standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton),
        )
        self._show_keyboard_shortcuts_action = self._create_action(
            "Keyboard Shortcuts",
            self._show_keyboard_shortcuts,
        )
        self._show_about_dialog_action = self._create_action(
            "About",
            self._show_about_dialog,
            icon=style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation),
        )

    def _setup_menu_bar(self) -> None:
        """Set up the application menu bar."""
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self._new_action)
        file_menu.addAction(self._open_action)
        file_menu.addAction(self._save_action)
        file_menu.addAction(self._save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self._exit_action)

        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction(self._undo_action)
        edit_menu.addAction(self._redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self._cut_action)
        edit_menu.addAction(self._copy_action)
        edit_menu.addAction(self._paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self._add_content_action)
        edit_menu.addAction(self._delete_selected_content_action)
        edit_menu.addAction(self._select_all_content_action)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self._show_documentation_action)
        help_menu.addAction(self._show_keyboard_shortcuts_action)
        help_menu.addSeparator()
        help_menu.addAction(self._show_about_dialog_action)

    def _setup_toolbar(self) -> None:
        """Set up the application toolbar."""
        toolbar = QToolBar("Main Toolbar", self)
        self.addToolBar(toolbar)

        toolbar.addAction(self._new_action)
        toolbar.addAction(self._open_action)
        toolbar.addAction(self._save_action)
        toolbar.addSeparator()
        toolbar.addAction(self._add_content_action)
        toolbar.addAction(self._delete_selected_content_action)

    def _setup_project_explorer(self) -> None:
        """Set up the application dock widgets."""
        self._project_explorer = ProjectExplorer(self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._project_explorer)

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
        pass

    def _open_project(self) -> None:
        """Open an existing project."""
        pass

    def _save_project(self) -> None:
        """Save the current project."""
        pass

    def _save_project_as(self) -> None:
        """Save the current project to a new location."""
        pass

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

    def _add_content(self) -> None:
        """Add content to the active view."""
        pass

    def _delete_selected_content(self) -> None:
        """Delete the selected content."""
        pass

    def _select_all_content(self) -> None:
        """Select all available content."""
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
