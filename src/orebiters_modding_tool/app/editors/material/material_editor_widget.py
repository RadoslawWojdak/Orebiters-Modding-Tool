from collections.abc import Sequence

from PySide6.QtWidgets import QWidget

from orebiters_modding_tool.app.editors.content.content_editor_widget import ContentEditorWidget
from orebiters_modding_tool.app.editors.crafting.material_requirement_editor_widget import (
    MaterialRequirementEditorWidget,
)
from orebiters_modding_tool.app.editors.editor_field import EditorField, EditorVariantField
from orebiters_modding_tool.app.editors.material.material_localization_editor_widget import (
    MaterialLocalizationEditorWidget,
)
from orebiters_modding_tool.app.widgets.list_widget import ListWidget
from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.material import Material


class MaterialEditorWidget(ContentEditorWidget[Material]):
    """Editor for a material."""

    CONTENT_TYPE = ContentType.MATERIALS

    def _can_add_material_requirement(self) -> bool:
        """Return whether another material requirement can be added.

        :returns: Whether at least one available material reference exists.
        :raises TypeError: If the material references provider is invalid.
        """
        return MaterialRequirementEditorWidget.can_create_item(self._context)

    FIELDS: tuple[EditorField | EditorVariantField, ...] = (
        EditorField(
            name="qualified_id",
            label="Qualified ID:",
            read_only=True,
            value_provider=ContentEditorWidget._get_qualified_id,
        ),
        EditorField(
            name="localizations",
            label="Localizations",
            editor_widget_type=MaterialLocalizationEditorWidget,
        ),
        EditorField(
            name="crafting_materials",
            label="Crafting Materials",
            item_factory=MaterialRequirementEditorWidget.create_default_item,
            editor_widget_type=MaterialRequirementEditorWidget,
            can_add_provider=_can_add_material_requirement,
        ),
    )

    def __init__(
        self,
        item: Material,
        context: dict[str, object] | None = None,
        parent: QWidget | None = None,
        *,
        read_only: bool = False,
        show_save_button: bool = True,
    ) -> None:
        """Initialize the material editor.

        :param item: Material to edit.
        :param context: Additional context required by the editor.
        :param parent: Parent widget.
        :param read_only: Whether the editor is read-only.
        :param show_save_button: Whether to display the save button.
        """
        context = {} if context is None else context.copy()
        context["excluded_material_references_provider"] = self._get_excluded_material_references

        super().__init__(
            item,
            context,
            parent,
            read_only=read_only,
            show_save_button=show_save_button,
        )

    def _get_excluded_material_references(
        self,
        current_material: ContentReference | None,
    ) -> Sequence[ContentReference]:
        """Return material references that cannot be selected.

        :param current_material: Reference selected by the current requirement.
        :returns: Material references excluded from the available choices.
        """
        excluded_references = {
            self._get_material_reference(),
            *self._get_used_material_references(),
        }
        excluded_references.discard(current_material)

        return tuple(excluded_references)

    def _get_material_reference(self) -> ContentReference:
        """Return a reference to the edited material."""
        return ContentReference(
            content_type=Material.CONTENT_TYPE,
            qualified_id=self._get_qualified_id(),
        )

    def _get_used_material_references(self) -> Sequence[ContentReference]:
        """Return material references currently used in crafting materials."""
        widget = self._get_field_widget("crafting_materials")

        if not isinstance(widget, ListWidget):
            return ()

        return MaterialRequirementEditorWidget.get_selected_references(widget)
