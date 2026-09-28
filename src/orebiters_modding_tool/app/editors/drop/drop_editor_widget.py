from collections.abc import Sequence

from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget
from orebiters_modding_tool.app.editors.editor_field import EditorField, EditorVariantField
from orebiters_modding_tool.domain.content import ContentReference
from orebiters_modding_tool.domain.mineable import Drop


class DropEditorWidget(BaseEditorWidget[Drop]):
    """Editor for a drop."""

    def _get_item_choices(
        self,
        current_item: ContentReference | None,
    ) -> Sequence[ContentReference]:
        """Return available item references.

        :param current_item: Reference selected by the current drop.
        :returns: Available item references.
        """
        item_references = self._get_item_references()

        excluded_provider = self._context.get("excluded_item_references_provider")

        if not callable(excluded_provider):
            return item_references

        excluded_references = excluded_provider(current_item)

        return tuple(
            reference for reference in item_references if reference not in excluded_references
        )

    @staticmethod
    def _format_item_choice(choice: object) -> str:
        """Format an item reference choice.

        :param choice: Choice to format.
        :returns: Formatted item reference.
        :raises TypeError: If the choice is not a content reference.
        """
        if not isinstance(choice, ContentReference):
            raise TypeError("Item choice must be a ContentReference.")

        return choice.qualified_id or ""

    FIELDS: tuple[EditorField | EditorVariantField, ...] = (
        EditorField(
            name="item",
            label="Item:",
            value_type=ContentReference,
            choices_provider=_get_item_choices,
            choice_formatter=_format_item_choice,
        ),
        EditorField(
            name="probability",
            label="Probability:",
            value_type=float,
        ),
    )

    def _get_item_references(self) -> Sequence[ContentReference]:
        """Return registered item references from context."""
        provider = self._context.get("item_references_provider")

        if not callable(provider):
            raise TypeError("Context value 'item_references_provider' must be callable.")

        item_references = provider()

        if not isinstance(item_references, Sequence):
            raise TypeError("Item references provider must return a sequence.")

        return item_references
