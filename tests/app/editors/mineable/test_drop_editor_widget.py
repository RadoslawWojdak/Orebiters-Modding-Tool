from typing import cast

import pytest
from PySide6.QtWidgets import QApplication, QComboBox, QDoubleSpinBox

from orebiters_modding_tool.app.editors.mineable.drop_editor_widget import DropEditorWidget
from orebiters_modding_tool.domain.content import ContentReference
from tests.factories.content import ContentReferenceFactory
from tests.factories.drop import DropFactory


@pytest.fixture
def item_references() -> tuple[ContentReference, ...]:
    """Create item references for tests."""
    return tuple(ContentReferenceFactory.create() for _ in range(3))


def _create_context(
    item_references: tuple[ContentReference, ...],
    *,
    excluded_item_references_provider=None,
) -> dict[str, object]:
    """Create drop editor context for tests."""
    context = {
        "item_references_provider": lambda: item_references,
    }

    if excluded_item_references_provider is not None:
        context["excluded_item_references_provider"] = excluded_item_references_provider

    return context


def test_creates_item_choices_from_context(
    qapp: QApplication,
    item_references: tuple[ContentReference, ...],
) -> None:
    """Create item choices from the configured context provider."""
    drop = DropFactory.create(item=item_references[0])
    editor = DropEditorWidget(drop, context=_create_context(item_references))

    item_widget = cast(QComboBox, editor._get_field_widget("item"))

    assert item_widget.count() == len(item_references)
    assert {item_widget.itemData(index) for index in range(item_widget.count())} == set(
        item_references
    )


def test_formats_item_choices_using_qualified_id(qapp: QApplication) -> None:
    """Display qualified IDs for item choices."""
    item = ContentReferenceFactory.create(qualified_id="test.test_mod.materials.iron_ore")

    assert DropEditorWidget._format_item_choice(item) == "test.test_mod.materials.iron_ore"


def test_formats_category_reference_as_empty_string(
    qapp: QApplication,
    materials_category_reference: ContentReference,
) -> None:
    """Display an empty string for category references."""
    assert DropEditorWidget._format_item_choice(materials_category_reference) == ""


def test_excludes_references_from_excluded_provider(
    qapp: QApplication,
    item_references: tuple[ContentReference, ...],
) -> None:
    """Exclude references returned by the excluded-items provider."""
    excluded = item_references[1]

    editor = DropEditorWidget(
        DropFactory.create(item=item_references[0]),
        context=_create_context(
            item_references,
            excluded_item_references_provider=lambda current_item: (excluded,),
        ),
    )

    item_widget = cast(QComboBox, editor._get_field_widget("item"))

    available_references = {item_widget.itemData(index) for index in range(item_widget.count())}

    assert excluded not in available_references
    assert item_references[0] in available_references
    assert item_references[2] in available_references


def test_uses_all_references_without_excluded_provider(
    qapp: QApplication,
    item_references: tuple[ContentReference, ...],
) -> None:
    """Use all item references when no exclusion provider is configured."""
    editor = DropEditorWidget(
        DropFactory.create(item=item_references[0]),
        context=_create_context(item_references),
    )

    item_widget = cast(QComboBox, editor._get_field_widget("item"))

    available_references = {item_widget.itemData(index) for index in range(item_widget.count())}

    assert available_references == set(item_references)


def test_saves_selected_item_and_probability(
    qapp: QApplication,
    item_references: tuple[ContentReference, ...],
) -> None:
    """Save the selected item and probability."""
    drop = DropFactory.create(item=item_references[0], probability=0.5)
    editor = DropEditorWidget(drop, context=_create_context(item_references))

    item_widget = cast(QComboBox, editor._get_field_widget("item"))
    probability_widget = cast(QDoubleSpinBox, editor._get_field_widget("probability"))

    item_widget.setCurrentIndex(2)
    probability_widget.setValue(0.75)

    editor.save()

    assert drop.item == item_references[2]
    assert drop.probability == 0.75


def test_raises_when_item_references_provider_is_missing(qapp: QApplication) -> None:
    """Raise when the item references provider is missing."""
    drop = DropFactory.create()

    with pytest.raises(TypeError, match="item_references_provider"):
        DropEditorWidget(drop, context={})


def test_raises_when_item_references_provider_is_not_callable(qapp: QApplication) -> None:
    """Raise when the item references provider is not callable."""
    drop = DropFactory.create()

    with pytest.raises(TypeError, match="item_references_provider"):
        DropEditorWidget(drop, context={"item_references_provider": "invalid"})


def test_raises_when_item_references_provider_returns_non_sequence(qapp: QApplication) -> None:
    """Raise when the item references provider returns a non-sequence."""
    drop = DropFactory.create()

    with pytest.raises(TypeError, match="sequence"):
        DropEditorWidget(drop, context={"item_references_provider": lambda: object()})


def test_raises_when_formatting_invalid_item_choice(qapp: QApplication):
    """Raise when an invalid item choice is formatted."""
    with pytest.raises(TypeError, match="ContentReference"):
        DropEditorWidget._format_item_choice("invalid")
