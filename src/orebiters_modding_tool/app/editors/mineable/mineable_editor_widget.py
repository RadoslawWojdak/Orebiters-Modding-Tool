from collections.abc import Sequence
from typing import cast

from PySide6.QtWidgets import QWidget

from orebiters_modding_tool.app.editors.content.content_editor_widget import ContentEditorWidget
from orebiters_modding_tool.app.editors.content.content_localization_editor_widget import (
    ContentLocalizationEditorWidget,
)
from orebiters_modding_tool.app.editors.editor_field import (
    EditorField,
    EditorVariant,
    EditorVariantField,
)
from orebiters_modding_tool.app.editors.mineable.drop_editor_widget import DropEditorWidget
from orebiters_modding_tool.app.widgets.dynamic_combo_box import DynamicComboBox
from orebiters_modding_tool.app.widgets.list_widget import ListWidget
from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.material import Material
from orebiters_modding_tool.domain.mineable import Drop, Mineable, MineableType


class MineableEditorWidget(ContentEditorWidget[Mineable]):
    """Editor for a mineable."""

    CONTENT_TYPE = ContentType.MINEABLES

    def _get_qualified_id(self) -> str:
        """Return the qualified mineable ID."""
        mod_id = self._context["mod_id"]

        if not isinstance(mod_id, str):
            raise TypeError("Context value 'mod_id' must be a string.")

        return self._item.get_qualified_id(mod_id)

    @staticmethod
    def _create_drop(context: dict[str, object]) -> Drop:
        """Create a default drop.

        :param context: Editor context.
        :returns: New drop.
        """
        item_references = MineableEditorWidget._get_registered_item_references(context)

        excluded_provider = context.get("excluded_item_references_provider")
        excluded_references = excluded_provider(None) if callable(excluded_provider) else ()

        available_references = tuple(
            reference for reference in item_references if reference not in excluded_references
        )

        if not available_references:
            raise ValueError("Cannot create a drop without available item references.")

        return Drop(available_references[0], 1.0)

    def _can_add_drop(self) -> bool:
        """Return whether another drop can be added."""
        item_references = self._get_registered_item_references(self._context)
        excluded_references = self._get_excluded_item_references(None)

        return any(reference not in excluded_references for reference in item_references)

    FIELDS: tuple[EditorField | EditorVariantField, ...] = (
        EditorField(
            name="qualified_id",
            label="Qualified ID:",
            read_only=True,
            value_provider=_get_qualified_id,
        ),
        EditorField(
            name="localizations",
            label="Localizations",
            editor_widget_type=ContentLocalizationEditorWidget,
        ),
        EditorField(
            name="type",
            label="Type:",
            value_type=MineableType,
            choices_provider=lambda self, _current_value: tuple(MineableType),
            choice_formatter=lambda choice: cast(MineableType, choice).singular_display_name,
        ),
        EditorField(
            name="tier",
            label="Tier:",
            value_type=int,
        ),
        EditorField(
            name="value",
            label="Value:",
            value_type=int | None,
        ),
        EditorField(
            name="hardness",
            label="Hardness:",
            value_type=int,
        ),
        EditorField(
            name="min_drill_power",
            label="Minimum Drill Power:",
            value_type=int,
        ),
        EditorField(
            name="min_depth",
            label="Minimum Depth:",
            value_type=int | None,
        ),
        EditorField(
            name="max_depth",
            label="Maximum Depth:",
            value_type=int | None,
        ),
        EditorVariantField(
            label="Generation Strategy:",
            variants=(
                EditorVariant(
                    label="Peak Depth",
                    fields=(
                        EditorField(
                            name="peak_depth",
                            label="Peak Depth:",
                            value_type=int,
                        ),
                    ),
                ),
                EditorVariant(
                    label="Weight Range",
                    fields=(
                        EditorField(
                            name="start_weight",
                            label="Start Weight:",
                            value_type=float,
                        ),
                        EditorField(
                            name="end_weight",
                            label="End Weight:",
                            value_type=float,
                        ),
                    ),
                ),
                EditorVariant(
                    label="Rarity",
                    fields=(
                        EditorField(
                            name="rarity",
                            label="Rarity:",
                            value_type=float,
                        ),
                    ),
                ),
            ),
        ),
        EditorField(
            name="drops",
            label="Drops",
            item_factory=_create_drop,
            editor_widget_type=DropEditorWidget,
            can_add_provider=_can_add_drop,
        ),
        EditorField(
            name="particle_colors",
            label="Particle Colors",
            value_type=list[str],
        ),
        EditorField(
            name="damage_multiplier",
            label="Damage Multiplier:",
            value_type=float,
        ),
        EditorField(
            name="player_only_destruction",
            label="Player Only Destruction:",
            value_type=bool,
        ),
    )

    def __init__(
        self,
        item: Mineable,
        context: dict[str, object] | None = None,
        parent: QWidget | None = None,
        *,
        read_only: bool = False,
        show_save_button: bool = True,
    ) -> None:
        """Initialize the mineable editor."""
        context = {} if context is None else context.copy()
        context["excluded_item_references_provider"] = self._get_excluded_item_references

        super().__init__(
            item,
            context,
            parent,
            read_only=read_only,
            show_save_button=show_save_button,
        )

    def _get_excluded_item_references(
        self,
        current_item: ContentReference | None,
    ) -> Sequence[ContentReference]:
        """Return item references that cannot be selected.

        :param current_item: Reference selected by the current drop.
        :returns: Excluded item references.
        """
        excluded_references = set(self._get_used_item_references())
        excluded_references.discard(current_item)

        return tuple(excluded_references)

    def _get_used_item_references(self) -> Sequence[ContentReference]:
        """Return item references currently used in drops."""
        drops_widget = self._get_field_widget("drops")

        if not isinstance(drops_widget, ListWidget):
            return ()

        used_references: list[ContentReference] = []

        for index in range(drops_widget.item_count()):
            item_widget = drops_widget.item_at(index)

            if not isinstance(item_widget, DropEditorWidget):
                raise TypeError("Drop item must be a DropEditorWidget.")

            item_field = item_widget._get_field_widget("item")

            if not isinstance(item_field, DynamicComboBox):
                raise TypeError("Item field must be a DynamicComboBox.")

            item_reference = item_field.currentData()

            if isinstance(item_reference, ContentReference):
                used_references.append(item_reference)

        return tuple(used_references)

    @staticmethod
    def _get_registered_item_references(context: dict[str, object]) -> Sequence[ContentReference]:
        """Return currently registered item references.

        :param context: Editor context.
        :returns: Currently registered item references.
        """
        provider = context.get("item_references_provider")

        if not callable(provider):
            raise TypeError("Context value 'item_references_provider' must be callable.")

        item_references = provider()

        if not isinstance(item_references, Sequence):
            raise TypeError("Item references provider must return a sequence.")

        if not all(
            isinstance(reference, ContentReference)
            and reference.content_type == Material.CONTENT_TYPE
            for reference in item_references
        ):
            raise TypeError("Item references provider must return only material references.")

        return item_references
