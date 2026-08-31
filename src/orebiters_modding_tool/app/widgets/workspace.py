from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from orebiters_modding_tool.app.widgets.welcome_widget import WelcomeWidget


class Workspace(QWidget):
    """Central workspace of the application."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._setup_layout()
        self._setup_tab_widget()
        self._setup_welcome_tab()

    def _setup_layout(self) -> None:
        """Set up the workspace layout."""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

    def _setup_tab_widget(self) -> None:
        """Set up the workspace tab widget."""
        self._tab_widget = QTabWidget(self)
        self._tab_widget.setTabsClosable(True)

        self._tab_widget.tabCloseRequested.connect(self._close_tab)

        self._layout.addWidget(self._tab_widget)

    def _setup_welcome_tab(self) -> None:
        """Set up the welcome tab."""
        welcome_widget = WelcomeWidget(self)

        self._tab_widget.addTab(welcome_widget, "Welcome")

    def _close_tab(self, index: int) -> None:
        """Close the tab at the specified index.

        :param index: Index of the tab to close.
        :returns: None.
        """
        self._tab_widget.removeTab(index)
