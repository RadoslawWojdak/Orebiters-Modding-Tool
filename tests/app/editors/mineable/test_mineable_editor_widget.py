from typing import cast

import pytest
from PySide6.QtWidgets import QApplication, QComboBox, QLabel, QLineEdit, QSpinBox

from orebiters_modding_tool.app.editors import MineableEditorWidget
from orebiters_modding_tool.app.editors.mineable.drop_editor_widget import DropEditorWidget
from orebiters_modding_tool.app.widgets.list_widget import ListWidget
from orebiters_modding_tool.app.widgets.variant_widget import VariantWidget
from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.mineable import MineableType
from tests.factories.content import ContentReferenceFactory
from tests.factories.drop import DropFactory
from tests.factories.mineable import MineableFactory


def _create_context(
    item_references: tuple[ContentReference, ...] = (),
    *,
    mod_id: str = "test.test_mod",
) -> dict[str, object]:
    return {
        "mod_id": mod_id,
        "item_references_provider": lambda: item_references,
    }


def test_creates_editor_with_mineable_data(qapp: QApplication) -> None:
    """Create an editor populated with the mineable data."""
    mineable = MineableFactory.create(
        type=MineableType.RESOURCE,
        tier=3,
        value=25,
        hardness=5,
        min_drill_power=4,
    )

    editor = MineableEditorWidget(mineable, context=_create_context())

    assert cast(QComboBox, editor._get_field_widget("type")).currentData() == MineableType.RESOURCE
    assert cast(QSpinBox, editor._get_field_widget("tier")).value() == 3
    assert cast(QLineEdit, editor._get_field_widget("value")).text() == "25"
    assert cast(QSpinBox, editor._get_field_widget("hardness")).value() == 5
    assert cast(QSpinBox, editor._get_field_widget("min_drill_power")).value() == 4


def test_displays_qualified_id(qapp: QApplication) -> None:
    """Display the mineable qualified ID using the configured mod ID."""
    mineable = MineableFactory.create(id="iron_ore")
    editor = MineableEditorWidget(mineable, context=_create_context(mod_id="orebiters.core"))

    qualified_id_widget = editor._get_field_widget("qualified_id")

    assert isinstance(qualified_id_widget, QLabel)
    assert qualified_id_widget.text() == "orebiters.core.mineables.iron_ore"


def test_selects_peak_depth_generation_strategy(qapp: QApplication) -> None:
    """Select the peak-depth variant when peak depth is populated."""
    mineable = MineableFactory.create(
        peak_depth=50,
        start_weight=None,
        end_weight=None,
        rarity=None,
    )
    editor = MineableEditorWidget(mineable, context=_create_context())

    variant_widget = editor.findChild(VariantWidget)

    assert variant_widget is not None
    assert variant_widget.active_index == 0


def test_selects_weight_range_generation_strategy(qapp: QApplication) -> None:
    """Select the weight-range variant when both weights are populated."""
    mineable = MineableFactory.create(
        peak_depth=None,
        start_weight=0.2,
        end_weight=0.8,
        rarity=None,
    )
    editor = MineableEditorWidget(mineable, context=_create_context())

    variant_widget = editor.findChild(VariantWidget)

    assert variant_widget is not None
    assert variant_widget.active_index == 1


def test_selects_rarity_generation_strategy(qapp: QApplication) -> None:
    """Select the rarity variant when rarity is populated."""
    mineable = MineableFactory.create(
        peak_depth=None,
        start_weight=None,
        end_weight=None,
        rarity=0.15,
    )

    editor = MineableEditorWidget(mineable, context=_create_context())

    variant_widget = editor.findChild(VariantWidget)

    assert variant_widget is not None
    assert variant_widget.active_index == 2


def test_rejects_ambiguous_generation_strategy(qapp: QApplication) -> None:
    """Reject a mineable when multiple generation strategies are populated."""
    mineable = MineableFactory.create(
        peak_depth=50,
        start_weight=0.2,
        end_weight=0.8,
        rarity=None,
    )

    with pytest.raises(ValueError, match="Multiple variants have populated fields"):
        MineableEditorWidget(mineable, context=_create_context())


def test_creates_drop_from_available_item_references(qapp: QApplication) -> None:
    """Create a drop using the first available item reference."""
    item_references = tuple(ContentReferenceFactory.create() for _ in range(2))
    mineable = MineableFactory.create()
    editor = MineableEditorWidget(mineable, context=_create_context(item_references))

    drops_widget = cast(ListWidget, editor._get_field_widget("drops"))
    drops_widget._add_button.click()

    assert drops_widget.item_count() == 1

    drop_editor = cast(DropEditorWidget, drops_widget.item_at(0))
    item_widget = cast(QComboBox, drop_editor._get_field_widget("item"))

    assert item_widget.currentData() == item_references[0]


def test_does_not_allow_adding_drop_without_available_items(qapp: QApplication) -> None:
    """Disable adding drops when no item references are available."""
    mineable = MineableFactory.create()
    editor = MineableEditorWidget(mineable, context=_create_context())

    drops_widget = cast(ListWidget, editor._get_field_widget("drops"))

    assert not drops_widget._add_button.isEnabled()


def test_excludes_items_already_used_by_other_drops(qapp: QApplication) -> None:
    """Exclude item references already used by another drop."""
    item_references = tuple(ContentReferenceFactory.create() for _ in range(2))
    existing_drop = DropFactory.create(item=item_references[0])

    mineable = MineableFactory.create(drops=[existing_drop])
    editor = MineableEditorWidget(mineable, context=_create_context(item_references))

    drops_widget = cast(ListWidget, editor._get_field_widget("drops"))
    first_drop_editor = cast(DropEditorWidget, drops_widget.item_at(0))

    item_widget = cast(QComboBox, first_drop_editor._get_field_widget("item"))

    assert item_widget.currentData() == item_references[0]

    drops_widget._add_button.click()

    second_drop_editor = cast(DropEditorWidget, drops_widget.item_at(1))
    second_item_widget = cast(QComboBox, second_drop_editor._get_field_widget("item"))

    assert second_item_widget.currentData() == item_references[1]


def test_keeps_current_drop_item_available(qapp: QApplication) -> None:
    """Keep the current drop item available while editing that drop."""
    item_references = tuple(ContentReferenceFactory.create() for _ in range(2))
    existing_drop = DropFactory.create(item=item_references[0])

    mineable = MineableFactory.create(drops=[existing_drop])
    editor = MineableEditorWidget(mineable, context=_create_context(item_references))

    drops_widget = cast(ListWidget, editor._get_field_widget("drops"))
    drop_editor = cast(DropEditorWidget, drops_widget.item_at(0))
    item_widget = cast(QComboBox, drop_editor._get_field_widget("item"))

    available_references = {item_widget.itemData(index) for index in range(item_widget.count())}

    assert item_references[0] in available_references
    assert item_references[1] in available_references


def test_saves_edited_mineable(qapp: QApplication) -> None:
    """Save edited mineable values through the editor."""
    mineable = MineableFactory.create(tier=1, hardness=5)
    editor = MineableEditorWidget(mineable, context=_create_context())

    cast(QSpinBox, editor._get_field_widget("tier")).setValue(4)
    cast(QSpinBox, editor._get_field_widget("hardness")).setValue(10)
    cast(QLineEdit, editor._get_field_widget("value")).setText("25")

    editor.save()

    assert mineable.tier == 4
    assert mineable.hardness == 10
    assert mineable.value == 25


def test_raises_when_mod_id_is_not_string(qapp: QApplication) -> None:
    """Raise when the mod ID context value is not a string."""
    mineable = MineableFactory.create()

    with pytest.raises(TypeError, match="mod_id"):
        MineableEditorWidget(
            mineable,
            context={"mod_id": 123, "item_references_provider": lambda: ()},
        )


def test_raises_when_item_references_provider_is_missing(qapp: QApplication) -> None:
    """Raise when the item references provider is missing."""
    mineable = MineableFactory.create()

    with pytest.raises(TypeError, match="item_references_provider"):
        MineableEditorWidget(mineable, context={"mod_id": "test.test_mod"})


def test_raises_when_item_references_provider_returns_invalid_items(qapp: QApplication) -> None:
    """Raise when the item references provider returns invalid references."""
    invalid_reference = ContentReferenceFactory.create(content_type=ContentType.MINEABLES)

    with pytest.raises(TypeError, match="material references"):
        MineableEditorWidget._get_registered_item_references(
            {"item_references_provider": lambda: (invalid_reference,)}
        )


def test_raises_when_item_references_provider_returns_non_sequence(qapp: QApplication) -> None:
    """Raise when the item references provider returns a non-sequence."""
    with pytest.raises(TypeError, match="sequence"):
        MineableEditorWidget._get_registered_item_references(
            {"item_references_provider": lambda: object()}
        )
