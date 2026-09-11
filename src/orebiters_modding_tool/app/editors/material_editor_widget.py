from collections.abc import Sequence

from PySide6.QtWidgets import QWidget

from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget
from orebiters_modding_tool.app.editors.editor_field import EditorField
from orebiters_modding_tool.app.editors.material_localization_editor_widget import (
    MaterialLocalizationEditorWidget,
)
from orebiters_modding_tool.app.editors.material_requirement_editor_widget import (
    MaterialRequirementEditorWidget,
)
from orebiters_modding_tool.app.widgets.dynamic_combo_box import DynamicComboBox
from orebiters_modding_tool.app.widgets.list_widget import ListWidget
from orebiters_modding_tool.domain.content import ContentReference
from orebiters_modding_tool.domain.material import Material, MaterialRequirement


class MaterialEditorWidget(BaseEditorWidget[Material]):
    """Editor for a material."""

    def _get_qualified_id(self) -> str:
        """Return the qualified material ID.

        :returns: Qualified material ID.
        """
        mod_id = self._context["mod_id"]

        if not isinstance(mod_id, str):
            raise TypeError("Context value 'mod_id' must be a string.")

        return self._item.get_qualified_id(mod_id)

    @staticmethod
    def _create_material_requirement(context: dict[str, object]) -> MaterialRequirement:
        """Create a default material requirement.

        :param context: Editor context.
        :returns: New material requirement.
        """
        material_references = MaterialEditorWidget._get_registered_material_references(context)

        excluded_provider = context.get("excluded_material_references_provider")
        excluded_references = excluded_provider(None) if callable(excluded_provider) else ()

        available_references = tuple(
            reference for reference in material_references if reference not in excluded_references
        )

        if not available_references:
            raise ValueError(
                "Cannot create a material requirement without available material references.",
            )

        return MaterialRequirement(available_references[0], 1)

    def _can_add_material_requirement(self) -> bool:
        """Return whether another material requirement can be added."""
        material_references = self._get_registered_material_references(self._context)
        excluded_references = self._get_excluded_material_references(None)

        return any(reference not in excluded_references for reference in material_references)

    FIELDS = (
        EditorField(
            name="qualified_id",
            label="Qualified ID:",
            read_only=True,
            value_provider=_get_qualified_id,
        ),
        EditorField(
            name="localizations",
            label="Localizations",
            editor_widget_type=MaterialLocalizationEditorWidget,
        ),
        EditorField(
            name="crafting_materials",
            label="Crafting Materials",
            item_factory=_create_material_requirement,
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
        """Initialize the material editor."""
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
        """Return material references that cannot be selected in the current widget.

        :param current_material: Reference to the widget's current material.
        :returns: Sequence of material references that cannot be selected.
        """
        excluded_references = {
            self._get_material_reference(),
            *self._get_used_material_references(),
        }

        excluded_references.discard(current_material)

        return tuple(excluded_references)

    def _get_used_material_references(self) -> Sequence[ContentReference]:
        """Return material references currently used in crafting materials."""
        crafting_materials = self._fields.get("crafting_materials")

        if not isinstance(crafting_materials, ListWidget):
            return ()

        used_references: list[ContentReference] = []

        for index in range(crafting_materials.item_count()):
            item_widget = crafting_materials.item_at(index)

            if not isinstance(item_widget, MaterialRequirementEditorWidget):
                raise TypeError("Crafting material item must be a MaterialRequirementEditorWidget.")

            material_field = item_widget._fields["material_reference"]

            if not isinstance(material_field, DynamicComboBox):
                raise TypeError("Material field must be a DynamicComboBox.")

            material_reference = material_field.currentData()

            if isinstance(material_reference, ContentReference):
                used_references.append(material_reference)

        return tuple(used_references)

    def _get_material_reference(self) -> ContentReference:
        """Return a reference to the edited material."""
        return ContentReference(
            content_type=Material.CONTENT_TYPE,
            qualified_id=self._get_qualified_id(),
        )

    @staticmethod
    def _get_registered_material_references(
        context: dict[str, object],
    ) -> Sequence[ContentReference]:
        """Return currently registered material references.

        :param context: Editor context.
        :returns: Currently registered material references.
        """
        provider = context.get("material_references_provider")

        if not callable(provider):
            raise TypeError("Context value 'material_references_provider' must be callable.")

        material_references = provider()

        if not isinstance(material_references, Sequence):
            raise TypeError("Material references provider must return a sequence.")

        return material_references
