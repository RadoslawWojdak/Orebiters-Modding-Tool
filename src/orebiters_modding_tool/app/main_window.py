from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget


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

    def _setup_central_widget(self) -> None:
        """Set up the central application widget."""
        central_widget = QWidget()
        self._main_layout = QVBoxLayout(central_widget)

        self.setCentralWidget(central_widget)

    def _setup_actions(self) -> None:
        """Set up the application actions."""
        self._new_action = QAction("New", self)
        self._new_action.setShortcut(QKeySequence.StandardKey.New)

        self._open_action = QAction("Open", self)
        self._open_action.setShortcut(QKeySequence.StandardKey.Open)

        self._save_action = QAction("Save", self)
        self._save_action.setShortcut(QKeySequence.StandardKey.Save)

        self._save_as_action = QAction("Save As", self)
        self._save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)

        self._exit_action = QAction("Exit", self)
        self._exit_action.setShortcut(QKeySequence.StandardKey.Quit)

        self._undo_action = QAction("Undo", self)
        self._undo_action.setShortcut(QKeySequence.StandardKey.Undo)

        self._redo_action = QAction("Redo", self)
        self._redo_action.setShortcut(QKeySequence.StandardKey.Redo)

        self._cut_action = QAction("Cut", self)
        self._cut_action.setShortcut(QKeySequence.StandardKey.Cut)

        self._copy_action = QAction("Copy", self)
        self._copy_action.setShortcut(QKeySequence.StandardKey.Copy)

        self._paste_action = QAction("Paste", self)
        self._paste_action.setShortcut(QKeySequence.StandardKey.Paste)

        self._delete_action = QAction("Delete", self)
        self._delete_action.setShortcut(QKeySequence.StandardKey.Delete)

        self._select_all_action = QAction("Select All", self)
        self._select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)

        self._show_documentation_action = QAction("Documentation", self)

        self._show_keyboard_shortcuts_action = QAction("Keyboard Shortcuts", self)

        self._show_about_dialog_action = QAction("About", self)

        self._new_action.triggered.connect(self._new_project)
        self._open_action.triggered.connect(self._open_project)
        self._save_action.triggered.connect(self._save_project)
        self._save_as_action.triggered.connect(self._save_project_as)
        self._exit_action.triggered.connect(self._exit_application)
        self._undo_action.triggered.connect(self._undo)
        self._redo_action.triggered.connect(self._redo)
        self._cut_action.triggered.connect(self._cut)
        self._copy_action.triggered.connect(self._copy)
        self._paste_action.triggered.connect(self._paste)
        self._delete_action.triggered.connect(self._delete_selection)
        self._select_all_action.triggered.connect(self._select_all)
        self._show_documentation_action.triggered.connect(self._show_documentation)
        self._show_keyboard_shortcuts_action.triggered.connect(self._show_keyboard_shortcuts)
        self._show_about_dialog_action.triggered.connect(self._show_about_dialog)

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
        edit_menu.addAction(self._delete_action)
        edit_menu.addAction(self._select_all_action)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self._show_documentation_action)
        help_menu.addAction(self._show_keyboard_shortcuts_action)
        help_menu.addSeparator()
        help_menu.addAction(self._show_about_dialog_action)

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

    def _delete_selection(self) -> None:
        """Delete the selected content."""
        pass

    def _select_all(self) -> None:
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
