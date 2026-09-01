from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from orebiters_modding_tool.app.widgets.content_overview import (
    ContentOverviewConfig,
    ContentOverviewWidget,
)
from orebiters_modding_tool.app.widgets.welcome_widget import WelcomeWidget
from orebiters_modding_tool.domain.content import ContentReference


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

    def open_content(self, content_reference: ContentReference) -> None:
        """Open content in the workspace.

        :param content_reference: Reference to the content to open.
        """
        existing_index = self._find_content_tab(content_reference)

        if existing_index is not None:
            self._tab_widget.setCurrentIndex(existing_index)
            return

        content_widget = self._create_content_widget(content_reference)
        tab_name = self._get_tab_name(content_reference)
        tab_index = self._tab_widget.addTab(content_widget, tab_name)

        self._tab_widget.setCurrentIndex(tab_index)

    def _close_tab(self, index: int) -> None:
        """Close the tab at the specified index.

        :param index: Index of the tab to close.
        """
        self._tab_widget.removeTab(index)

    def _find_content_tab(self, content_reference: ContentReference) -> int | None:
        """Find an open tab for the specified content.

        :param content_reference: Reference to the content.
        :returns: Tab index if the content is open, otherwise None.
        """
        for index in range(self._tab_widget.count()):
            widget = self._tab_widget.widget(index)

            if (
                isinstance(widget, ContentOverviewWidget)
                and widget.content_reference == content_reference
            ):
                return index

        return None

    def _create_content_widget(self, content_reference: ContentReference) -> QWidget:
        """Create a widget for the specified content.

        :param content_reference: Reference to the content.
        :returns: Configured content widget.
        """
        config = ContentOverviewConfig(
            title=self._get_tab_name(content_reference),
            empty_message="No content available.",
        )

        return ContentOverviewWidget(content_reference, config, self)

    @staticmethod
    def _get_tab_name(content_reference: ContentReference) -> str:
        """Get the tab name for the specified content.

        :param content_reference: Reference to the content.
        :returns: Tab name.
        """
        content_type_name = content_reference.content_type.value.replace("_", " ").title()

        if content_reference.content_id is None:
            return content_type_name

        return f"{content_type_name} {content_reference.content_id}"
