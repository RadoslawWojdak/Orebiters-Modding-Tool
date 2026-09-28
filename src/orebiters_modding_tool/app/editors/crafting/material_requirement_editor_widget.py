from collections.abc import Sequence

from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget
from orebiters_modding_tool.app.editors.editor_field import EditorField, EditorVariantField
from orebiters_modding_tool.app.widgets.dynamic_combo_box import DynamicComboBox
from orebiters_modding_tool.app.widgets.list_widget import ListWidget
from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.material import MaterialRequirement


class MaterialRequirementEditorWidget(BaseEditorWidget[MaterialRequirement]):
    """Editor for a material requirement."""

    def _get_material_choices(
        self,
        current_material: ContentReference | None,
    ) -> Sequence[ContentReference]:
        """Return available material references for the selection field.

        :param current_material: Currently selected material reference.
        :returns: Material references that are not excluded.
        :raises TypeError: If the material references provider is invalid.
        """
        references = self.get_registered_material_references(self._context)

        excluded_provider = self._context.get("excluded_material_references_provider")

        if not callable(excluded_provider):
            return references

        excluded_references = excluded_provider(current_material)

        return tuple(reference for reference in references if reference not in excluded_references)

    @staticmethod
    def _format_material_choice(choice: object) -> str:
        """Format a material reference for display.

        :param choice: Choice to format.
        :returns: Qualified ID of the material, or an empty string if unavailable.
        :raises TypeError: If the choice is not a content reference.
        """
        if not isinstance(choice, ContentReference):
            raise TypeError("Material choice must be a ContentReference.")

        return choice.qualified_id or ""

    FIELDS: tuple[EditorField | EditorVariantField, ...] = (
        EditorField(
            name="material_reference",
            label="Material",
            value_type=ContentReference,
            choices_provider=_get_material_choices,
            choice_formatter=_format_material_choice,
        ),
        EditorField(
            name="amount",
            label="Amount",
            value_type=int,
        ),
    )

    # =========================================================================
    # Public API
    # =========================================================================

    @staticmethod
    def get_registered_material_references(
        context: dict[str, object],
    ) -> Sequence[ContentReference]:
        """Return registered material references from the context.

        :param context: Editor context.
        :returns: Registered material references.
        :raises TypeError: If the provider or its returned references are invalid.
        """
        provider = context.get("material_references_provider")

        if not callable(provider):
            raise TypeError("Context value 'material_references_provider' must be callable.")

        references = provider()

        if not isinstance(references, Sequence):
            raise TypeError("Material references provider must return a sequence.")

        if not all(
            isinstance(reference, ContentReference)
            and reference.content_type == ContentType.MATERIALS
            for reference in references
        ):
            raise TypeError("Material references provider must return only material references.")

        return references

    @classmethod
    def create_default_item(cls, context: dict[str, object]) -> MaterialRequirement:
        """Create a default material requirement.

        :param context: Editor context.
        :returns: New material requirement using the first available material.
        :raises TypeError: If the material references provider is invalid.
        :raises ValueError: If no available material references exist.
        """
        references = cls.get_registered_material_references(context)

        excluded_provider = context.get("excluded_material_references_provider")
        excluded_references = excluded_provider(None) if callable(excluded_provider) else ()

        available_references = tuple(
            reference for reference in references if reference not in excluded_references
        )

        if not available_references:
            raise ValueError(
                "Cannot create a material requirement without available material references.",
            )

        return MaterialRequirement(available_references[0], 1)

    @classmethod
    def can_create_item(cls, context: dict[str, object]) -> bool:
        """Return whether another material requirement can be added.

        :param context: Editor context.
        :returns: Whether at least one material reference is available.
        :raises TypeError: If the material references provider is invalid.
        """
        references = cls.get_registered_material_references(context)

        excluded_provider = context.get("excluded_material_references_provider")
        excluded_references = excluded_provider(None) if callable(excluded_provider) else ()

        return any(reference not in excluded_references for reference in references)

    @classmethod
    def get_selected_references(cls, list_widget: ListWidget) -> Sequence[ContentReference]:
        """Return material references selected in a list of requirements.

        :param list_widget: List widget containing material requirement editors.
        :returns: Selected material references.
        :raises TypeError: If a list item or its material field has an unexpected type.
        """
        references: list[ContentReference] = []

        for index in range(list_widget.item_count()):
            item_widget = list_widget.item_at(index)

            if not isinstance(item_widget, cls):
                raise TypeError("Crafting material item must be a MaterialRequirementEditorWidget.")

            material_field = item_widget._get_field_widget("material_reference")

            if not isinstance(material_field, DynamicComboBox):
                raise TypeError("Material field must be a DynamicComboBox.")

            reference = material_field.currentData()

            if isinstance(reference, ContentReference):
                references.append(reference)

        return tuple(references)
