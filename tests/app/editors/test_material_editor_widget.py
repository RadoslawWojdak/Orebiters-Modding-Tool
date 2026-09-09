import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from orebiters_modding_tool.app.editors.material_editor_widget import MaterialEditorWidget
from orebiters_modding_tool.app.editors.material_requirement_editor_widget import (
    MaterialRequirementEditorWidget,
)
from orebiters_modding_tool.app.widgets.dynamic_combo_box import DynamicComboBox
from orebiters_modding_tool.app.widgets.list_widget import ListWidget
from orebiters_modding_tool.domain.material import MaterialRequirement
from tests.factories.content import ContentReferenceFactory
from tests.factories.material import MaterialFactory


def test_displays_qualified_id(qapp: object) -> None:
    """Display the qualified material ID."""
    material = MaterialFactory.create(id="iron")

    editor = MaterialEditorWidget(
        material,
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [],
        },
    )

    qualified_id_field = editor._fields["qualified_id"]

    assert isinstance(qualified_id_field, QLabel)
    assert qualified_id_field.text() == "orebiters.core.iron"


def test_create_material_requirement_uses_first_available_reference(qapp: object) -> None:
    """Create a material requirement using the first available reference."""
    current_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.iron")
    first_available_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.copper")
    second_available_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.gold")

    requirement = MaterialEditorWidget._create_material_requirement(
        {
            "material_references_provider": lambda: [
                current_reference,
                first_available_reference,
                second_available_reference,
            ],
            "excluded_material_references_provider": lambda _: (current_reference,),
        },
    )

    assert isinstance(requirement, MaterialRequirement)
    assert requirement.material == first_available_reference
    assert requirement.amount == 1


def test_create_material_requirement_raises_without_available_references(qapp: object) -> None:
    """Raise an error when no material references are available."""
    reference = ContentReferenceFactory.create(qualified_id="orebiters.core.iron")

    with pytest.raises(
        ValueError,
        match="Cannot create a material requirement without available material references.",
    ):
        MaterialEditorWidget._create_material_requirement(
            {
                "material_references_provider": lambda: [reference],
                "excluded_material_references_provider": lambda _: (reference,),
            },
        )


def test_material_requirement_excludes_current_material(qapp: object) -> None:
    """Exclude the edited material from material requirement choices."""
    material = MaterialFactory.create(id="iron")
    other_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.copper")

    editor = MaterialEditorWidget(
        material,
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [
                ContentReferenceFactory.create(qualified_id="orebiters.core.iron"),
                other_reference,
            ],
        },
    )

    crafting_materials = editor._fields["crafting_materials"]

    assert isinstance(crafting_materials, ListWidget)

    crafting_materials._add_item()

    item_widget = crafting_materials.item_at(0)
    assert isinstance(item_widget, MaterialRequirementEditorWidget)

    material_field = item_widget._fields["material"]
    assert isinstance(material_field, DynamicComboBox)

    material_field.showPopup()
    material_field.hidePopup()

    choices = [material_field.itemData(index) for index in range(material_field.count())]

    assert all(reference.qualified_id != "orebiters.core.iron" for reference in choices)
    assert other_reference in choices


def test_material_requirement_excludes_already_used_materials(qapp: object) -> None:
    """Exclude materials already used in another crafting requirement."""
    used_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.copper")
    available_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.gold")

    material = MaterialFactory.create(id="iron")

    editor = MaterialEditorWidget(
        material,
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [
                ContentReferenceFactory.create(qualified_id="orebiters.core.iron"),
                used_reference,
                available_reference,
            ],
        },
    )

    crafting_materials = editor._fields["crafting_materials"]

    assert isinstance(crafting_materials, ListWidget)

    crafting_materials._add_item()

    assert crafting_materials.item_count() == 1

    first_item = crafting_materials.item_at(0)
    assert isinstance(first_item, MaterialRequirementEditorWidget)

    first_material_field = first_item._fields["material"]
    assert isinstance(first_material_field, DynamicComboBox)

    first_material_field.setCurrentIndex(first_material_field.find_data_equal(used_reference))

    crafting_materials._add_item()

    assert crafting_materials.item_count() == 2

    second_item = crafting_materials.item_at(1)
    assert isinstance(second_item, MaterialRequirementEditorWidget)

    second_material_field = second_item._fields["material"]
    assert isinstance(second_material_field, DynamicComboBox)

    second_material_field.showPopup()
    second_material_field.hidePopup()

    choices = [
        second_material_field.itemData(index) for index in range(second_material_field.count())
    ]

    assert used_reference not in choices
    assert available_reference in choices


def test_material_requirement_keeps_its_current_material_available(qapp: object) -> None:
    """Keep the current material available when refreshing its choices."""
    current_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.copper")
    other_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.gold")

    material = MaterialFactory.create(id="iron")

    editor = MaterialEditorWidget(
        material,
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [
                ContentReferenceFactory.create(qualified_id="orebiters.core.iron"),
                current_reference,
                other_reference,
            ],
        },
    )

    crafting_materials = editor._fields["crafting_materials"]

    assert isinstance(crafting_materials, ListWidget)

    crafting_materials._add_item()

    assert crafting_materials.item_count() == 1

    item_widget = crafting_materials.item_at(0)
    assert isinstance(item_widget, MaterialRequirementEditorWidget)

    material_field = item_widget._fields["material"]
    assert isinstance(material_field, DynamicComboBox)

    material_field.setCurrentIndex(material_field.find_data_equal(current_reference))

    assert material_field.currentData() == current_reference

    material_field.showPopup()
    material_field.hidePopup()

    choices = [material_field.itemData(index) for index in range(material_field.count())]

    assert current_reference in choices
    assert other_reference in choices


def test_get_used_material_references_returns_current_values(qapp: object) -> None:
    """Return material references currently used in crafting materials."""
    first_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.copper")
    second_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.gold")

    material = MaterialFactory.create(id="iron")

    editor = MaterialEditorWidget(
        material,
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [
                first_reference,
                second_reference,
            ],
        },
    )

    crafting_materials = editor._fields["crafting_materials"]

    assert isinstance(crafting_materials, ListWidget)

    crafting_materials._add_item()
    crafting_materials._add_item()

    assert crafting_materials.item_count() == 2

    first_item = crafting_materials.item_at(0)
    second_item = crafting_materials.item_at(1)

    assert isinstance(first_item, MaterialRequirementEditorWidget)
    assert isinstance(second_item, MaterialRequirementEditorWidget)

    first_material_field = first_item._fields["material"]
    second_material_field = second_item._fields["material"]

    assert isinstance(first_material_field, DynamicComboBox)
    assert isinstance(second_material_field, DynamicComboBox)

    first_material_field.setCurrentIndex(first_material_field.find_data_equal(first_reference))
    second_material_field.setCurrentIndex(second_material_field.find_data_equal(second_reference))

    assert editor._get_used_material_references() == (first_reference, second_reference)


def test_refresh_uses_updated_material_references(qapp: object) -> None:
    """Refresh the editor using current material references."""
    references: list = []

    editor = MaterialEditorWidget(
        MaterialFactory.create(id="iron"),
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: references,
        },
    )

    crafting_materials = editor._fields["crafting_materials"]

    assert isinstance(crafting_materials, ListWidget)
    assert not crafting_materials._add_button.isEnabled()

    references.append(ContentReferenceFactory.create(qualified_id="orebiters.core.copper"))

    editor.refresh()

    assert crafting_materials._add_button.isEnabled()


def test_read_only_disables_adding_material_requirements(qapp: object) -> None:
    """Disable adding material requirements in read-only mode."""
    reference = ContentReferenceFactory.create(qualified_id="orebiters.core.copper")

    editor = MaterialEditorWidget(
        MaterialFactory.create(id="iron"),
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [reference],
        },
        read_only=True,
    )

    crafting_materials = editor._fields["crafting_materials"]

    assert isinstance(crafting_materials, ListWidget)
    assert not crafting_materials._add_button.isEnabled()


def test_read_only_makes_qualified_id_selectable(qapp: object) -> None:
    """Allow selecting the qualified ID in read-only mode."""
    material = MaterialFactory.create()

    editor = MaterialEditorWidget(
        material,
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [],
        },
        read_only=True,
    )

    qualified_id_field = editor._fields["qualified_id"]

    assert isinstance(qualified_id_field, QLabel)
    assert qualified_id_field.textInteractionFlags() == Qt.TextInteractionFlag.TextSelectableByMouse
