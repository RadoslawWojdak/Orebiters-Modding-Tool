from collections.abc import Sequence

from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget
from orebiters_modding_tool.app.editors.editor_field import EditorField
from orebiters_modding_tool.domain.content import ContentReference
from orebiters_modding_tool.domain.material import MaterialRequirement


class MaterialRequirementEditorWidget(BaseEditorWidget[MaterialRequirement]):
    """Editor for a material requirement."""

    def _get_material_choices(
        self,
        current_material: ContentReference | None,
    ) -> Sequence[ContentReference]:
        """Return available material references.

        :returns: Available material references.
        :raises TypeError: If material references are invalid.
        """
        material_references = self._get_material_references()

        excluded_provider = self._context.get("excluded_material_references_provider")

        if not callable(excluded_provider):
            return material_references

        excluded_references = excluded_provider(current_material)

        return tuple(
            reference for reference in material_references if reference not in excluded_references
        )

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
            name="material_reference",
            label="Material",
            choices_provider=_get_material_choices,
            choice_formatter=_format_material_choice,
        ),
        EditorField(
            name="amount",
            label="Amount",
        ),
    )

    def _get_material_references(self) -> Sequence[ContentReference]:
        """Return current material references from the context provider."""
        provider = self._context.get("material_references_provider")

        if not callable(provider):
            raise TypeError("Context value 'material_references_provider' must be callable.")

        material_references = provider()

        if not isinstance(material_references, Sequence):
            raise TypeError("Material references provider must return a sequence.")

        return material_references
