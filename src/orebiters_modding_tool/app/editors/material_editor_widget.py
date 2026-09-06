from collections.abc import Sequence

from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget
from orebiters_modding_tool.app.editors.editor_field import EditorField
from orebiters_modding_tool.app.editors.material_localization_editor_widget import (
    MaterialLocalizationEditorWidget,
)
from orebiters_modding_tool.app.editors.material_requirement_editor_widget import (
    MaterialRequirementEditorWidget,
)
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
        material_references = context["material_references"]

        if not isinstance(material_references, Sequence):
            raise TypeError("Context value 'material_references' must be a sequence.")

        if not material_references:
            raise ValueError("Cannot create a material requirement without material references.")

        return MaterialRequirement(material_references[0], 1)

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
        ),
    )
