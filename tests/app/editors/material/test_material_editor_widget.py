import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from orebiters_modding_tool.app.editors.material.material_editor_widget import MaterialEditorWidget
from orebiters_modding_tool.app.editors.material.material_requirement_editor_widget import (
    MaterialRequirementEditorWidget,
)
from orebiters_modding_tool.app.widgets.dynamic_combo_box import DynamicComboBox
from orebiters_modding_tool.app.widgets.list_widget import ListWidget
from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.material import MaterialRequirement
from tests.factories.content import ContentReferenceFactory
from tests.factories.material import MaterialFactory


def test_displays_qualified_id(qapp: QApplication) -> None:
    """Display the qualified material ID."""
    material = MaterialFactory.create(id="iron")

    editor = MaterialEditorWidget(
        material,
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [],
        },
    )

    qualified_id_widget = editor._get_field_widget("qualified_id")

    assert isinstance(qualified_id_widget, QLabel)
    assert qualified_id_widget.text() == "orebiters.core.materials.iron"


def test_get_qualified_id_raises_when_mod_id_is_not_string(qapp: QApplication) -> None:
    """Raise an error when the mod ID is not a string."""
    with pytest.raises(TypeError, match="Context value 'mod_id' must be a string."):
        MaterialEditorWidget(
            MaterialFactory.create(id="iron"),
            context={
                "mod_id": 123,
                "material_references_provider": lambda: [],
            },
        )


def test_create_material_requirement_uses_first_available_reference(qapp: QApplication) -> None:
    """Create a material requirement using the first available reference."""
    current_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.iron")
    first_available_reference = ContentReferenceFactory.create(
        qualified_id="orebiters.core.materials.copper"
    )
    second_available_reference = ContentReferenceFactory.create(
        qualified_id="orebiters.core.materials.gold"
    )

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
    assert requirement.material_reference == first_available_reference
    assert requirement.amount == 1


def test_create_material_requirement_allows_reference_without_excluded_provider(
    qapp: QApplication,
) -> None:
    """Create a material requirement without an exclusion provider."""
    reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.copper")
    requirement = MaterialEditorWidget._create_material_requirement(
        {"material_references_provider": lambda: [reference]},
    )

    assert requirement == MaterialRequirement(reference, 1)


def test_create_material_requirement_raises_without_available_references(
    qapp: QApplication,
) -> None:
    """Raise an error when no material references are available."""
    reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.iron")

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


def test_material_requirement_excludes_current_material(qapp: QApplication) -> None:
    """Exclude the edited material from material requirement choices."""
    material = MaterialFactory.create(id="iron")
    other_reference = ContentReferenceFactory.create(
        content_type=ContentType.MATERIALS,
        qualified_id="orebiters.core.materials.copper",
    )

    editor = MaterialEditorWidget(
        material,
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [
                ContentReferenceFactory.create(
                    content_type=ContentType.MATERIALS,
                    qualified_id="orebiters.core.materials.iron",
                ),
                other_reference,
            ],
        },
    )

    crafting_materials = editor._get_field_widget("crafting_materials")

    assert isinstance(crafting_materials, ListWidget)

    crafting_materials._add_item()

    item_widget = crafting_materials.item_at(0)
    assert isinstance(item_widget, MaterialRequirementEditorWidget)

    material_field = item_widget._get_field_widget("material_reference")
    assert isinstance(material_field, DynamicComboBox)

    material_field.showPopup()
    material_field.hidePopup()

    choices = [material_field.itemData(index) for index in range(material_field.count())]

    assert all(reference.qualified_id != "orebiters.core.materials.iron" for reference in choices)
    assert other_reference in choices


def test_material_requirement_excludes_already_used_materials(qapp: QApplication) -> None:
    """Exclude materials already used in another crafting requirement."""
    used_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.copper")
    available_reference = ContentReferenceFactory.create(
        qualified_id="orebiters.core.materials.gold"
    )

    material = MaterialFactory.create(id="iron")

    editor = MaterialEditorWidget(
        material,
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [
                ContentReferenceFactory.create(qualified_id="orebiters.core.materials.iron"),
                used_reference,
                available_reference,
            ],
        },
    )

    crafting_materials = editor._get_field_widget("crafting_materials")

    assert isinstance(crafting_materials, ListWidget)

    crafting_materials._add_item()

    assert crafting_materials.item_count() == 1

    first_item = crafting_materials.item_at(0)
    assert isinstance(first_item, MaterialRequirementEditorWidget)

    first_material_field = first_item._get_field_widget("material_reference")
    assert isinstance(first_material_field, DynamicComboBox)

    first_material_field.setCurrentIndex(first_material_field.find_data_equal(used_reference))

    crafting_materials._add_item()

    assert crafting_materials.item_count() == 2

    second_item = crafting_materials.item_at(1)
    assert isinstance(second_item, MaterialRequirementEditorWidget)

    second_material_field = second_item._get_field_widget("material_reference")
    assert isinstance(second_material_field, DynamicComboBox)

    second_material_field.showPopup()
    second_material_field.hidePopup()

    choices = [
        second_material_field.itemData(index) for index in range(second_material_field.count())
    ]

    assert used_reference not in choices
    assert available_reference in choices


def test_material_requirement_keeps_its_current_material_available(qapp: QApplication) -> None:
    """Keep the current material available when refreshing its choices."""
    current_reference = ContentReferenceFactory.create(
        qualified_id="orebiters.core.materials.copper"
    )
    other_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.gold")

    material = MaterialFactory.create(id="iron")

    editor = MaterialEditorWidget(
        material,
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [
                ContentReferenceFactory.create(qualified_id="orebiters.core.materials.iron"),
                current_reference,
                other_reference,
            ],
        },
    )

    crafting_materials = editor._get_field_widget("crafting_materials")

    assert isinstance(crafting_materials, ListWidget)

    crafting_materials._add_item()

    assert crafting_materials.item_count() == 1

    item_widget = crafting_materials.item_at(0)
    assert isinstance(item_widget, MaterialRequirementEditorWidget)

    material_field = item_widget._get_field_widget("material_reference")
    assert isinstance(material_field, DynamicComboBox)

    material_field.setCurrentIndex(material_field.find_data_equal(current_reference))

    assert material_field.currentData() == current_reference

    material_field.showPopup()
    material_field.hidePopup()

    choices = [material_field.itemData(index) for index in range(material_field.count())]

    assert current_reference in choices
    assert other_reference in choices


def test_removed_material_requirement_makes_reference_available_again(qapp: QApplication) -> None:
    """Make a material reference available again after removing its requirement."""
    used_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.copper")
    available_reference = ContentReferenceFactory.create(
        qualified_id="orebiters.core.materials.gold"
    )

    editor = MaterialEditorWidget(
        MaterialFactory.create(id="iron"),
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [
                ContentReferenceFactory.create(qualified_id="orebiters.core.materials.iron"),
                used_reference,
                available_reference,
            ],
        },
    )

    crafting_materials = editor._get_field_widget("crafting_materials")

    assert isinstance(crafting_materials, ListWidget)

    crafting_materials._add_item()

    first_item = crafting_materials.item_at(0)
    assert isinstance(first_item, MaterialRequirementEditorWidget)

    first_material_field = first_item._get_field_widget("material_reference")
    assert isinstance(first_material_field, DynamicComboBox)

    first_material_field.setCurrentIndex(first_material_field.find_data_equal(used_reference))

    crafting_materials._add_item()

    assert crafting_materials.item_count() == 2

    second_item = crafting_materials.item_at(1)
    assert isinstance(second_item, MaterialRequirementEditorWidget)

    second_material_field = second_item._get_field_widget("material_reference")
    assert isinstance(second_material_field, DynamicComboBox)

    second_material_field.showPopup()
    second_material_field.hidePopup()

    choices = [
        second_material_field.itemData(index) for index in range(second_material_field.count())
    ]

    assert used_reference not in choices
    assert available_reference in choices

    crafting_materials._remove_buttons[0].click()

    assert crafting_materials.item_count() == 1

    second_material_field.showPopup()
    second_material_field.hidePopup()

    choices = [
        second_material_field.itemData(index) for index in range(second_material_field.count())
    ]

    assert used_reference in choices
    assert available_reference in choices


def test_get_used_material_references_returns_current_values(qapp: QApplication) -> None:
    """Return material references currently used in crafting materials."""
    first_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.copper")
    second_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.gold")

    material = MaterialFactory.create(id="iron")

    editor = MaterialEditorWidget(
        material,
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [first_reference, second_reference],
        },
    )

    crafting_materials = editor._get_field_widget("crafting_materials")

    assert isinstance(crafting_materials, ListWidget)

    crafting_materials._add_item()
    crafting_materials._add_item()

    assert crafting_materials.item_count() == 2

    first_item = crafting_materials.item_at(0)
    second_item = crafting_materials.item_at(1)

    assert isinstance(first_item, MaterialRequirementEditorWidget)
    assert isinstance(second_item, MaterialRequirementEditorWidget)

    first_material_field = first_item._get_field_widget("material_reference")
    second_material_field = second_item._get_field_widget("material_reference")

    assert isinstance(first_material_field, DynamicComboBox)
    assert isinstance(second_material_field, DynamicComboBox)

    first_material_field.setCurrentIndex(first_material_field.find_data_equal(first_reference))
    second_material_field.setCurrentIndex(second_material_field.find_data_equal(second_reference))

    assert editor._get_used_material_references() == (first_reference, second_reference)


def test_get_used_material_references_returns_empty_without_crafting_materials_field(
    qapp: QApplication,
) -> None:
    """Return no used references when the crafting materials field is missing."""
    editor = MaterialEditorWidget(
        MaterialFactory.create(id="iron"),
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [],
        },
    )

    widget = editor._get_field_widget("crafting_materials")
    editor._widgets.remove(widget)

    assert editor._get_used_material_references() == ()


def test_get_used_material_references_raises_for_invalid_item_widget(qapp: QApplication) -> None:
    """Raise an error when a crafting material item has an invalid widget type."""
    editor = MaterialEditorWidget(
        MaterialFactory.create(id="iron"),
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [],
        },
    )

    crafting_materials = editor._get_field_widget("crafting_materials")

    assert isinstance(crafting_materials, ListWidget)

    crafting_materials._item_widgets.append(QWidget())

    with pytest.raises(
        TypeError,
        match="Crafting material item must be a MaterialRequirementEditorWidget.",
    ):
        editor._get_used_material_references()


def test_get_used_material_references_raises_for_invalid_material_field(qapp: QApplication) -> None:
    """Raise an error when a material field has an invalid widget type."""
    reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.copper")
    editor = MaterialEditorWidget(
        MaterialFactory.create(id="iron"),
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [reference],
        },
    )

    crafting_materials = editor._get_field_widget("crafting_materials")

    assert isinstance(crafting_materials, ListWidget)

    crafting_materials._add_item()

    item_widget = crafting_materials.item_at(0)

    assert isinstance(item_widget, MaterialRequirementEditorWidget)

    widget = item_widget._get_field_widget("material_reference")
    item_widget._widgets[item_widget._widgets.index(widget)] = QWidget()

    with pytest.raises(
        TypeError,
        match="Material field must be a DynamicComboBox.",
    ):
        editor._get_used_material_references()


def test_can_add_material_requirement_returns_false_when_no_reference_is_available(
    qapp: QApplication,
) -> None:
    """Prevent adding a requirement when every reference is excluded."""
    current_reference = ContentReferenceFactory.create(
        content_type=ContentType.MATERIALS,
        qualified_id="orebiters.core.materials.iron",
    )

    editor = MaterialEditorWidget(
        MaterialFactory.create(id="iron"),
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [current_reference],
        },
    )

    assert not editor._can_add_material_requirement()


def test_can_add_material_requirement_returns_true_when_reference_is_available(
    qapp: QApplication,
) -> None:
    """Allow adding a requirement when an unused reference is available."""
    current_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.iron")
    available_reference = ContentReferenceFactory.create(
        qualified_id="orebiters.core.materials.copper"
    )

    editor = MaterialEditorWidget(
        MaterialFactory.create(id="iron"),
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [
                current_reference,
                available_reference,
            ],
        },
    )

    assert editor._can_add_material_requirement()


def test_refresh_uses_updated_material_references(qapp: QApplication) -> None:
    """Refresh the editor using current material references."""
    references: list[ContentReference] = []

    editor = MaterialEditorWidget(
        MaterialFactory.create(id="iron"),
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: references,
        },
    )

    crafting_materials = editor._get_field_widget("crafting_materials")

    assert isinstance(crafting_materials, ListWidget)
    assert not crafting_materials._add_button.isEnabled()

    references.append(
        ContentReferenceFactory.create(qualified_id="orebiters.core.materials.copper")
    )

    editor.refresh()

    assert crafting_materials._add_button.isEnabled()


def test_get_registered_material_references_raises_without_provider(qapp: QApplication) -> None:
    """Raise an error when no material references provider is configured."""
    with pytest.raises(
        TypeError,
        match="Context value 'material_references_provider' must be callable.",
    ):
        MaterialEditorWidget._get_registered_material_references({})


def test_get_registered_material_references_raises_when_provider_returns_invalid_value(
    qapp: QApplication,
) -> None:
    """Raise an error when the material references provider returns a non-sequence."""
    with pytest.raises(TypeError, match="Material references provider must return a sequence."):
        MaterialEditorWidget._get_registered_material_references(
            {"material_references_provider": lambda: object()},
        )


def test_read_only_disables_adding_material_requirements(qapp: QApplication) -> None:
    """Disable adding material requirements in read-only mode."""
    reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.copper")

    editor = MaterialEditorWidget(
        MaterialFactory.create(id="iron"),
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [reference],
        },
        read_only=True,
    )

    crafting_materials = editor._get_field_widget("crafting_materials")

    assert isinstance(crafting_materials, ListWidget)
    assert not crafting_materials._add_button.isEnabled()


def test_read_only_makes_qualified_id_selectable(qapp: QApplication) -> None:
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

    qualified_id_field = editor._get_field_widget("qualified_id")

    assert isinstance(qualified_id_field, QLabel)
    assert qualified_id_field.textInteractionFlags() == Qt.TextInteractionFlag.TextSelectableByMouse
