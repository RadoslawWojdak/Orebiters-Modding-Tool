from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QMessageBox, QScrollArea, QTabWidget, QVBoxLayout, QWidget

from orebiters_modding_tool.app.dialogs.content_id_dialog import ContentIdDialog
from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget
from orebiters_modding_tool.app.events.content import ContentChange, ContentChangeType
from orebiters_modding_tool.app.models.content_factory import CONTENT_FACTORY_REGISTRY
from orebiters_modding_tool.app.models.content_table_model import ContentTableModel
from orebiters_modding_tool.app.widgets.content_overview import (
    ContentOverviewConfig,
    ContentOverviewWidget,
)
from orebiters_modding_tool.app.widgets.welcome_widget import WelcomeWidget
from orebiters_modding_tool.domain.content import (
    Content,
    ContentReference,
    ContentState,
    ContentType,
)
from orebiters_modding_tool.domain.material import Material
from orebiters_modding_tool.services.project_service import ProjectService


class Workspace(QWidget):
    """Central workspace of the application."""

    content_changed = Signal(ContentChange)

    def __init__(self, project_service: ProjectService, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._project_service = project_service

        self._setup_layout()
        self._setup_tab_widget()
        self._setup_welcome_tab()

    def refresh_current_content_state(self) -> None:
        """Refresh the content state display of the current tab."""
        widget = self._tab_widget.currentWidget()

        if isinstance(widget, ContentOverviewWidget):
            widget.refresh_content_states()

    def close_project_tabs(self) -> None:
        """Close all project-related tabs."""
        for index in reversed(range(self._tab_widget.count())):
            widget = self._tab_widget.widget(index)

            if isinstance(widget, ContentOverviewWidget):
                self._close_tab(index)
                continue

            if widget is not None and self._get_editor_from_tab(widget) is not None:
                self._close_tab(index)

    def _setup_layout(self) -> None:
        """Set up the workspace layout."""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

    def _setup_tab_widget(self) -> None:
        """Set up the workspace tab widget."""
        self._tab_widget = QTabWidget(self)
        self._tab_widget.setTabsClosable(True)
        self._tab_widget.tabCloseRequested.connect(self._close_tab)
        self._tab_widget.currentChanged.connect(self._refresh_current_tab)

        self._layout.addWidget(self._tab_widget)

    def _setup_welcome_tab(self) -> None:
        """Set up the welcome tab."""
        welcome_widget = WelcomeWidget(self)
        self._tab_widget.addTab(welcome_widget, "Welcome")

    # =========================================================================
    # Content
    # =========================================================================

    def open_content(self, content_reference: ContentReference) -> None:
        """Open the content represented by a reference.

        :param content_reference: Reference to the content or content category.
        """
        if content_reference.is_category:
            self._open_content_overview(content_reference)
            return

        self._open_content_editor(content_reference)

    def _open_content_overview(self, content_reference: ContentReference) -> None:
        """Open a content overview.

        :param content_reference: Reference to a content category.
        """
        existing_index = self._find_content_tab(content_reference)
        if existing_index is not None:
            self._tab_widget.setCurrentIndex(existing_index)
            return

        content_widget = self._create_content_widget(content_reference)
        tab_name = self._get_tab_name(content_reference)
        tab_index = self._tab_widget.addTab(content_widget, tab_name)
        self._tab_widget.setCurrentIndex(tab_index)

    def _open_content_editor(self, content_reference: ContentReference) -> None:
        """Open the editor for specific content.

        :param content_reference: Reference to the content to edit.
        """
        active_project = self._project_service.active_project
        if active_project is None:
            raise RuntimeError("No active project.")

        if content_reference.qualified_id is None:
            raise ValueError("Expected a reference to specific content.")

        content_id = content_reference.content_id

        for item in active_project.content[content_reference.content_type]:
            if item.id == content_id:
                self._edit_content(content_reference, [item])
                return

        raise ValueError(f"Content not found: {content_reference.qualified_id}.")

    def _create_content_widget(
        self,
        content_reference: ContentReference,
    ) -> ContentOverviewWidget[Any]:
        """Create a widget for the specified content.

        :param content_reference: Reference to the content.
        :returns: Configured content widget.
        """
        config = ContentOverviewConfig(
            title=self._get_tab_name(content_reference),
            empty_message="No content available.",
        )

        model = self._create_content_model(content_reference)

        content_widget = ContentOverviewWidget(
            content_reference=content_reference,
            config=config,
            model=model,
            parent=self,
        )

        content_widget.add_requested.connect(self._add_content)
        content_widget.edit_requested.connect(self._edit_content)
        content_widget.delete_requested.connect(self._delete_content)

        return content_widget

    def _create_content_model(self, content_reference: ContentReference) -> ContentTableModel[Any]:
        """Create a table model for the specified content.

        :param content_reference: Reference to the content.
        :returns: Configured content table model.
        :raises RuntimeError: If no project is active.
        :raises ValueError: If the content type is unsupported.
        """
        active_project = self._project_service.active_project

        if active_project is None:
            raise RuntimeError("No active project.")

        try:
            model_class = ContentTableModel.get_class(content_reference.content_type)
        except KeyError:
            raise ValueError(
                f"Unsupported content type: {content_reference.content_type}."
            ) from None

        content = active_project.content[content_reference.content_type]

        return model_class(content, self)

    # =========================================================================
    # Content CRUD
    # =========================================================================

    def _add_content(self, content_reference: ContentReference) -> None:
        """Open a dialog for creating a new content item.

        :param content_reference: Reference to the content.
        """
        ContentIdDialog(
            content_type=content_reference.content_type,
            on_create=lambda content_id: self._create_content(content_reference, content_id),
            parent=self,
        ).exec()

    def _create_content(self, content_reference: ContentReference, content_id: str) -> None:
        """Create and open a content editor.

        :param content_reference: Reference to the content.
        :param content_id: Content ID.
        :raises ValueError: If the content cannot be added.
        """
        item = self._create_content_item(content_reference, content_id)

        self._project_service.add_content(content_reference.content_type, item)

        content_widget = self._get_content_widget(content_reference)
        content_widget.model.add_item(item)

        project = self._project_service.active_project
        if project is None:
            raise RuntimeError("No active project.")

        self.content_changed.emit(
            ContentChange(
                change_type=ContentChangeType.CREATED,
                content_type=content_reference.content_type,
                content_name=item.get_qualified_id(project.qualified_id),
            ),
        )

        editor = self._create_content_editor(content_reference, item)
        editor_tab = self._create_editor_tab(editor)
        tab_index = self._tab_widget.addTab(editor_tab, self._get_editor_tab_name(item))
        self._tab_widget.setCurrentIndex(tab_index)

    def _edit_content(self, content_reference: ContentReference, items: list[Content[Any]]) -> None:
        """Open editors for selected content items.

        :param content_reference: Reference to the content.
        :param items: Content items to edit.
        """
        for item in items:
            existing_index = self._find_editor_tab(item)

            if existing_index is not None:
                self._tab_widget.setCurrentIndex(existing_index)
                continue

            editor = self._create_content_editor(content_reference, item)
            editor_tab = self._create_editor_tab(editor)
            tab_index = self._tab_widget.addTab(editor_tab, self._get_editor_tab_name(item))
            self._tab_widget.setCurrentIndex(tab_index)

    def _delete_content(
        self,
        content_reference: ContentReference,
        items: list[Content[Any]],
    ) -> None:
        """Delete selected content items.

        :param content_reference: Reference to the content.
        :param items: Content items to delete.
        """
        answer = QMessageBox.question(
            self,
            "Delete Content",
            f"Delete {len(items)} selected item(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        content_widget = self._get_content_widget(content_reference)
        model = content_widget.model

        removed_count = 0
        for item in items:
            row = self._find_item_row(model, item)

            if row is not None:
                self._close_editor_tab(item)
                self._project_service.remove_content(content_reference.content_type, item)
                model.remove_item(row)
                removed_count += 1

        if removed_count:
            self.content_changed.emit(
                ContentChange(
                    change_type=ContentChangeType.REMOVED,
                    content_type=content_reference.content_type,
                    count=removed_count,
                ),
            )

    # =========================================================================
    # Editors
    # =========================================================================

    @staticmethod
    def _create_content_item(content_reference: ContentReference, content_id: str) -> Content[Any]:
        """Create a new content item.

        :param content_reference: Reference to the content.
        :param content_id: Content ID.
        :returns: New content item.
        :raises ValueError: If the content type is unsupported.
        """
        factory = CONTENT_FACTORY_REGISTRY.get(content_reference.content_type)

        if factory is None:
            raise ValueError(f"Unsupported content type: {content_reference.content_type}.")

        return factory(content_id)

    def _create_content_editor(
        self,
        content_reference: ContentReference,
        item: Content[Any],
    ) -> BaseEditorWidget[Any]:
        """Create an editor for a content item.

        :param content_reference: Reference to the content.
        :param item: Content item to edit.
        :returns: Configured content editor.
        :raises ValueError: If the content type is unsupported.
        """
        content_type = content_reference.content_type

        try:
            editor_class = BaseEditorWidget.get_class(content_type)
        except KeyError:
            raise ValueError(f"Unsupported content type: {content_type}.") from None

        if content_type is ContentType.MATERIALS:
            if not isinstance(item, Material):
                raise TypeError("Expected a Material.")
            context = self._create_material_editor_context()
        else:
            raise ValueError(f"Unsupported content type: {content_type}.")

        editor = editor_class(item=item, context=context, parent=self)

        editor.saved.connect(lambda: self._handle_content_editor_saved(content_reference, item))

        return editor

    def _create_editor_tab(self, editor: BaseEditorWidget[Any]) -> QScrollArea:
        """Wrap an editor in a single scroll area.

        :param editor: Editor widget to wrap.
        :returns: Scroll area containing the complete editor.
        """
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidget(editor)

        return scroll_area

    def _create_material_editor_context(self) -> dict[str, object]:
        """Create context required by the material editor.

        :returns: Material editor context.
        """
        active_project = self._project_service.active_project

        if active_project is None:
            raise RuntimeError("No active project.")

        return {
            "mod_id": active_project.qualified_id,
            "material_references_provider": (
                lambda: self._project_service.get_content_references(ContentType.MATERIALS)
            ),
        }

    def _handle_content_editor_saved(
        self,
        content_reference: ContentReference,
        item: Content[Any],
    ) -> None:
        """Handle content saved from its editor.

        :param content_reference: Reference used to open the content.
        :param item: Content item saved by the editor.
        """
        if item.state is ContentState.SAVED:
            item.state = ContentState.MODIFIED

        self._project_service.mark_project_as_modified()

        project = self._project_service.active_project
        if project is None:
            raise RuntimeError("No active project.")

        self.content_changed.emit(
            ContentChange(
                change_type=ContentChangeType.UPDATED,
                content_type=content_reference.content_type,
                content_name=item.get_qualified_id(project.qualified_id),
            ),
        )

    # =========================================================================
    # Helpers
    # =========================================================================

    def _get_content_widget(
        self,
        content_reference: ContentReference,
    ) -> ContentOverviewWidget[Any]:
        """Return the open overview widget for the specified content.

        :param content_reference: Reference to the content.
        :returns: Content overview widget.
        """
        index = self._find_content_tab(content_reference)

        if index is None:
            raise RuntimeError(f"Content tab is not open: {content_reference}.")

        widget = self._tab_widget.widget(index)

        if not isinstance(widget, ContentOverviewWidget):
            raise RuntimeError(f"Invalid widget in content tab: {content_reference}.")

        return widget

    @staticmethod
    def _find_item_row(model: ContentTableModel[Any], item: Content[Any]) -> int | None:
        """Find the row containing an item.

        :param model: Table model.
        :param item: Item to find.
        :returns: Item row or None.
        """
        for row in range(model.rowCount()):
            if model.get_item(row) is item:
                return row

        return None

    def _refresh_current_tab(self, index: int) -> None:
        """Refresh the currently active tab."""
        widget = self._tab_widget.widget(index)
        if widget is None:
            return

        editor = self._get_editor_from_tab(widget)

        if editor is not None:
            editor.refresh()

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

    def _close_editor_tab(self, item: Content[Any]) -> None:
        """Close the editor tab for the specified content item.

        :param item: Content item being deleted.
        """
        index = self._find_editor_tab(item)

        if index is not None:
            self._close_tab(index)

    def _find_editor_tab(self, item: Content[Any]) -> int | None:
        """Find an open editor tab for the specified content item.

        :param item: Content item being edited.
        :returns: Tab index if the editor is open, otherwise None.
        """
        for index in range(self._tab_widget.count()):
            widget = self._tab_widget.widget(index)
            if widget is None:
                continue

            editor = self._get_editor_from_tab(widget)

            if editor is not None and editor.item is item:
                return index

        return None

    @staticmethod
    def _get_editor_from_tab(widget: QWidget) -> BaseEditorWidget[Any] | None:
        """Return the editor contained in a tab.

        :param widget: Tab widget.
        :returns: Editor if the tab contains one, otherwise None.
        """
        if isinstance(widget, BaseEditorWidget):
            return widget

        if isinstance(widget, QScrollArea):
            content_widget = widget.widget()

            if isinstance(content_widget, BaseEditorWidget):
                return content_widget

        return None

    @staticmethod
    def _get_editor_tab_name(item: Content[Any]) -> str:
        """Get the tab name for an editor.

        :param item: Content being edited.
        :returns: Editor tab name.
        """
        return f"{item.id}"

    def _close_tab(self, index: int) -> None:
        """Close the tab at the specified index."""
        self._tab_widget.removeTab(index)

    @staticmethod
    def _get_tab_name(content_reference: ContentReference) -> str:
        """Get the tab name for the specified content.

        :param content_reference: Reference to the content.
        :returns: Tab name.
        """
        content_type_name = content_reference.content_type.display_name

        if content_reference.qualified_id is None:
            return content_type_name

        return f"{content_type_name} {content_reference.content_id}"
