from typing import cast

import pytest
from PySide6.QtWidgets import QApplication, QSpinBox

from orebiters_modding_tool.app.editors.crafting.material_requirement_editor_widget import (
    MaterialRequirementEditorWidget,
)
from orebiters_modding_tool.app.widgets.dynamic_combo_box import DynamicComboBox
from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.material import MaterialRequirement
from tests.factories.content_factory import ContentReferenceFactory
from tests.factories.material_requirement_factory import MaterialRequirementFactory


def test_displays_material_and_amount(qapp: QApplication) -> None:
    """Display the selected material and required amount."""
    reference = ContentReferenceFactory.create("orebiters.core.materials.clay")
    requirement = MaterialRequirementFactory.create(reference, 3)

    editor = MaterialRequirementEditorWidget(
        requirement,
        context={"material_references_provider": lambda: [reference]},
    )

    material_field = editor._get_field_widget("material_reference")
    amount_field = cast(QSpinBox, editor._get_field_widget("amount"))

    assert isinstance(material_field, DynamicComboBox)
    assert material_field.currentData() == reference
    assert amount_field.value() == 3


def test_displays_available_material_choices(qapp: QApplication) -> None:
    """Display all available materials in the selection field."""
    first_reference = ContentReferenceFactory.create("orebiters.core.materials.clay")
    second_reference = ContentReferenceFactory.create("orebiters.core.materials.vitalite")

    editor = MaterialRequirementEditorWidget(
        MaterialRequirementFactory.create(first_reference),
        context={"material_references_provider": lambda: [first_reference, second_reference]},
    )

    field = editor._get_field_widget("material_reference")
    assert isinstance(field, DynamicComboBox)

    field.showPopup()
    field.hidePopup()

    choices = [field.itemData(i) for i in range(field.count())]

    assert choices == [first_reference, second_reference]


def test_excludes_references_provided_by_context(qapp: QApplication) -> None:
    """Exclude references returned by the exclusion provider."""
    first_reference = ContentReferenceFactory.create("orebiters.core.materials.clay")
    excluded_reference = ContentReferenceFactory.create("orebiters.core.materials.vitalite")
    third_reference = ContentReferenceFactory.create("orebiters.core.materials.stone")

    editor = MaterialRequirementEditorWidget(
        MaterialRequirementFactory.create(first_reference),
        context={
            "material_references_provider": lambda: [
                first_reference,
                excluded_reference,
                third_reference,
            ],
            "excluded_material_references_provider": lambda _: (excluded_reference,),
        },
    )

    field = editor._get_field_widget("material_reference")
    assert isinstance(field, DynamicComboBox)

    field.showPopup()
    field.hidePopup()

    choices = [field.itemData(i) for i in range(field.count())]

    assert choices == [first_reference, third_reference]


def test_refreshes_choices_using_current_provider_values(qapp: QApplication) -> None:
    """Refresh material choices when the provider values change."""
    first_reference = ContentReferenceFactory.create("orebiters.core.materials.clay")
    second_reference = ContentReferenceFactory.create("orebiters.core.materials.vitalite")
    references = [first_reference]

    editor = MaterialRequirementEditorWidget(
        MaterialRequirementFactory.create(first_reference),
        context={"material_references_provider": lambda: references},
    )

    field = editor._get_field_widget("material_reference")
    assert isinstance(field, DynamicComboBox)

    field.showPopup()
    field.hidePopup()
    assert [field.itemData(i) for i in range(field.count())] == [first_reference]

    references.append(second_reference)

    field.showPopup()
    field.hidePopup()
    assert [field.itemData(i) for i in range(field.count())] == [first_reference, second_reference]


def test_formats_material_choice_using_qualified_id() -> None:
    """Display a material reference using its qualified ID."""
    reference = ContentReferenceFactory.create("orebiters.core.materials.clay")

    assert MaterialRequirementEditorWidget._format_material_choice(reference) == (
        "orebiters.core.materials.clay"
    )


def test_formats_material_choice_without_qualified_id() -> None:
    """Display an empty string when a reference has no qualified ID."""
    reference = ContentReference(content_type=ContentType.MATERIALS, qualified_id=None)

    assert MaterialRequirementEditorWidget._format_material_choice(reference) == ""


def test_rejects_invalid_material_choice() -> None:
    """Reject a value that is not a content reference."""
    with pytest.raises(TypeError, match="Material choice must be a ContentReference."):
        MaterialRequirementEditorWidget._format_material_choice(object())


def test_get_registered_material_references_returns_provider_values() -> None:
    """Return material references supplied by the context."""
    references = [
        ContentReferenceFactory.create("orebiters.core.materials.clay"),
        ContentReferenceFactory.create("orebiters.core.materials.vitalite"),
    ]

    result = MaterialRequirementEditorWidget.get_registered_material_references(
        {"material_references_provider": lambda: references},
    )

    assert result == references


def test_get_registered_material_references_requires_provider() -> None:
    """Require a callable material references provider."""
    with pytest.raises(
        TypeError,
        match="Context value 'material_references_provider' must be callable.",
    ):
        MaterialRequirementEditorWidget.get_registered_material_references({})


@pytest.mark.parametrize(
    "provider",
    [
        lambda: object(),
        lambda: [object()],
        lambda: [ContentReferenceFactory.create("orebiters.core.items.clay")],
    ],
)
def test_get_registered_material_references_rejects_invalid_values(provider) -> None:
    """Reject invalid provider results and non-material references."""
    with pytest.raises(TypeError):
        MaterialRequirementEditorWidget.get_registered_material_references(
            {"material_references_provider": provider},
        )


def test_create_default_item_uses_first_available_reference() -> None:
    """Create a requirement using the first non-excluded material."""
    excluded_reference = ContentReferenceFactory.create("orebiters.core.materials.stone")
    first_available_reference = ContentReferenceFactory.create("orebiters.core.materials.clay")
    second_available_reference = ContentReferenceFactory.create("orebiters.core.materials.vitalite")
    context = {
        "material_references_provider": lambda: [
            excluded_reference,
            first_available_reference,
            second_available_reference,
        ],
        "excluded_material_references_provider": lambda _: (excluded_reference,),
    }

    requirement = MaterialRequirementEditorWidget.create_default_item(context)

    assert requirement == MaterialRequirement(first_available_reference, 1)


def test_create_default_item_works_without_exclusion_provider() -> None:
    """Create a requirement when no exclusion provider is configured."""
    reference = ContentReferenceFactory.create("orebiters.core.materials.clay")

    requirement = MaterialRequirementEditorWidget.create_default_item(
        {"material_references_provider": lambda: [reference]},
    )

    assert requirement == MaterialRequirement(reference, 1)


def test_create_default_item_raises_when_no_reference_is_available() -> None:
    """Reject creation when all material references are excluded."""
    reference = ContentReferenceFactory.create("orebiters.core.materials.stone")

    with pytest.raises(
        ValueError,
        match="Cannot create a material requirement without available material references.",
    ):
        MaterialRequirementEditorWidget.create_default_item(
            {
                "material_references_provider": lambda: [reference],
                "excluded_material_references_provider": lambda _: (reference,),
            },
        )


def test_can_create_item_returns_true_when_reference_is_available() -> None:
    """Allow creation when at least one material is available."""
    reference = ContentReferenceFactory.create("orebiters.core.materials.clay")

    assert MaterialRequirementEditorWidget.can_create_item(
        {"material_references_provider": lambda: [reference]},
    )


def test_can_create_item_returns_false_when_no_reference_is_available() -> None:
    """Prevent creation when all material references are excluded."""
    reference = ContentReferenceFactory.create("orebiters.core.materials.stone")

    assert not MaterialRequirementEditorWidget.can_create_item(
        {
            "material_references_provider": lambda: [reference],
            "excluded_material_references_provider": lambda _: (reference,),
        },
    )


def test_can_create_item_returns_false_when_no_references_are_registered() -> None:
    """Prevent creation when no material references are registered."""
    assert not MaterialRequirementEditorWidget.can_create_item(
        {"material_references_provider": lambda: []},
    )
