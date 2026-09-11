import pytest
from PySide6.QtWidgets import QApplication

from orebiters_modding_tool.app.editors.material_requirement_editor_widget import (
    MaterialRequirementEditorWidget,
)
from orebiters_modding_tool.app.widgets.dynamic_combo_box import DynamicComboBox
from orebiters_modding_tool.domain.content import ContentReference
from tests.factories.content import ContentReferenceFactory
from tests.factories.material_requirement import MaterialRequirementFactory


def test_displays_material_and_amount(qapp: QApplication) -> None:
    """Display the material and amount fields."""
    material_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.copper")
    requirement = MaterialRequirementFactory.create(material_reference, 3)

    editor = MaterialRequirementEditorWidget(
        requirement,
        context={"material_references_provider": lambda: [material_reference]},
    )

    material_field = editor._fields["material_reference"]
    amount_field = editor._fields["amount"]

    assert isinstance(material_field, DynamicComboBox)
    assert material_field.currentData() == material_reference
    assert amount_field.value() == 3


def test_get_material_choices_returns_all_references_without_exclusion_provider(
    qapp: QApplication,
) -> None:
    """Return all material references when no exclusion provider is configured."""
    first_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.copper")
    second_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.gold")

    editor = MaterialRequirementEditorWidget(
        MaterialRequirementFactory.create(first_reference),
        context={"material_references_provider": lambda: [first_reference, second_reference]},
    )

    assert editor._get_material_choices(first_reference) == [first_reference, second_reference]


def test_get_material_choices_excludes_references_from_provider(qapp: QApplication) -> None:
    """Exclude material references returned by the exclusion provider."""
    first_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.copper")
    excluded_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.gold")
    third_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.iron")

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

    assert editor._get_material_choices(first_reference) == (first_reference, third_reference)


def test_get_material_choices_passes_current_material_to_exclusion_provider(
    qapp: QApplication,
) -> None:
    """Pass the current material reference to the exclusion provider."""
    current_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.copper")
    other_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.gold")
    received_materials: list[ContentReference | None] = []

    editor = MaterialRequirementEditorWidget(
        MaterialRequirementFactory.create(current_reference),
        context={
            "material_references_provider": lambda: [current_reference, other_reference],
            "excluded_material_references_provider": lambda current_material: (
                received_materials.append(current_material) or ()
            ),
        },
    )

    choices = editor._get_material_choices(current_reference)

    assert choices == (current_reference, other_reference)
    assert received_materials == [None, current_reference]


def test_refreshes_material_choices_from_current_provider(qapp: QApplication) -> None:
    """Refresh material choices using the current provider values."""
    first_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.copper")
    second_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.gold")
    references = [first_reference]

    editor = MaterialRequirementEditorWidget(
        MaterialRequirementFactory.create(first_reference),
        context={"material_references_provider": lambda: references},
    )

    material_field = editor._fields["material_reference"]

    assert isinstance(material_field, DynamicComboBox)
    assert material_field.count() == 1
    assert material_field.itemData(0) == first_reference

    references.append(second_reference)

    material_field.showPopup()
    material_field.hidePopup()

    assert material_field.count() == 2
    assert material_field.itemData(0) == first_reference
    assert material_field.itemData(1) == second_reference


def test_format_material_choice_returns_qualified_id(qapp: QApplication) -> None:
    """Format a material choice using its qualified ID."""
    reference = ContentReferenceFactory.create(qualified_id="orebiters.core.copper")

    assert MaterialRequirementEditorWidget._format_material_choice(reference) == (
        "orebiters.core.copper"
    )


def test_format_material_choice_returns_empty_string_without_qualified_id(
    qapp: QApplication,
) -> None:
    """Return an empty string when a material reference has no qualified ID."""
    reference = ContentReference(
        content_type=ContentReferenceFactory.create().content_type,
        qualified_id=None,
    )

    assert MaterialRequirementEditorWidget._format_material_choice(reference) == ""


def test_format_material_choice_raises_for_invalid_choice(qapp: QApplication) -> None:
    """Raise an error when formatting an invalid material choice."""
    with pytest.raises(TypeError, match="Material choice must be a ContentReference."):
        MaterialRequirementEditorWidget._format_material_choice(object())


def test_get_material_references_raises_without_provider(qapp: QApplication) -> None:
    """Raise an error when no material references provider is configured."""
    with pytest.raises(
        TypeError,
        match="Context value 'material_references_provider' must be callable.",
    ):
        MaterialRequirementEditorWidget(MaterialRequirementFactory.create())


def test_get_material_references_raises_when_provider_returns_invalid_value(
    qapp: QApplication,
) -> None:
    """Raise an error when the material references provider returns a non-sequence."""
    with pytest.raises(TypeError, match="Material references provider must return a sequence."):
        MaterialRequirementEditorWidget(
            MaterialRequirementFactory.create(),
            context={"material_references_provider": lambda: object()},
        )
