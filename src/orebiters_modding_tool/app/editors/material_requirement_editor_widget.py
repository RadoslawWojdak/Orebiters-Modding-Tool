from collections.abc import Sequence

from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget
from orebiters_modding_tool.app.editors.editor_field import EditorField
from orebiters_modding_tool.domain.content import ContentReference
from orebiters_modding_tool.domain.material import MaterialRequirement


class MaterialRequirementEditorWidget(BaseEditorWidget[MaterialRequirement]):
    """Editor for a material requirement."""

    def _get_material_choices(self) -> Sequence[ContentReference]:
        """Return available material references.

        :returns: Available material references.
        :raises TypeError: If material references are invalid.
        """
        material_references = self._context.get("material_references")

        if not isinstance(material_references, Sequence):
            raise TypeError("Material references must be a sequence.")

        return material_references

    @staticmethod
    def _format_material_choice(choice: object) -> str:
        """Format a material reference choice.

        :param choice: Choice to format.
        :returns: Formatted material reference.
        :raises TypeError: If the choice is not a content reference.
        """
        if not isinstance(choice, ContentReference):
            raise TypeError("Material choice must be a ContentReference.")

        return choice.qualified_id or ""

    FIELDS = (
        EditorField(
            name="material",
            label="Material",
            choices_provider=_get_material_choices,
            choice_formatter=_format_material_choice,
        ),
        EditorField(
            name="amount",
            label="Amount",
        ),
    )
