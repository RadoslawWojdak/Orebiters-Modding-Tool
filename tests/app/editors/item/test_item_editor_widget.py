from PySide6.QtWidgets import QApplication

from orebiters_modding_tool.app.editors.crafting.material_requirement_editor_widget import (
    MaterialRequirementEditorWidget,
)
from orebiters_modding_tool.app.editors.item.item_editor_widget import ItemEditorWidget
from orebiters_modding_tool.app.widgets.dynamic_combo_box import DynamicComboBox
from orebiters_modding_tool.app.widgets.list_widget import ListWidget
from orebiters_modding_tool.domain.content import ContentReference
from tests.factories.content_factory import ContentReferenceFactory
from tests.factories.item_factory import ItemFactory


def _create_material_reference(material_id: str) -> ContentReference:
    """Create a material reference for editor tests."""
    return ContentReferenceFactory.create(f"orebiters.core.materials.{material_id}")


def _create_editor(
    item_id: str = "test_id",
    references: list[ContentReference] | None = None,
) -> ItemEditorWidget:
    """Create an item editor with registered material references."""
    return ItemEditorWidget(
        ItemFactory.create(id=item_id),
        context={
            "mod_id": "orebiters.core",
            "material_references_provider": lambda: [] if references is None else references,
        },
    )


def _get_crafting_materials(editor: ItemEditorWidget) -> ListWidget:
    """Return the crafting materials list."""
    widget = editor._get_field_widget("crafting_materials")
    assert isinstance(widget, ListWidget)
    return widget


def _get_material_field(editor: MaterialRequirementEditorWidget) -> DynamicComboBox:
    """Return the material selection field."""
    widget = editor._get_field_widget("material_reference")
    assert isinstance(widget, DynamicComboBox)
    return widget


def _get_available_choices(field: DynamicComboBox) -> list[ContentReference]:
    """Refresh and return the available material choices."""
    field.showPopup()
    field.hidePopup()
    return [field.itemData(index) for index in range(field.count())]


# =========================================================================
# Tests
# =========================================================================


def test_crafting_requirements_allow_all_registered_materials(qapp: QApplication) -> None:
    """Allow all registered materials when no requirements exist."""
    iron = _create_material_reference("iron")
    copper = _create_material_reference("copper")

    editor = _create_editor(references=[iron, copper])
    crafting_materials = _get_crafting_materials(editor)

    crafting_materials._add_button.click()

    requirement_editor = crafting_materials.item_at(0)
    assert isinstance(requirement_editor, MaterialRequirementEditorWidget)

    choices = _get_available_choices(_get_material_field(requirement_editor))

    assert choices == [iron, copper]


def test_crafting_requirements_exclude_materials_used_by_other_requirements(
    qapp: QApplication,
) -> None:
    """Prevent the same material from being selected more than once."""
    iron = _create_material_reference("iron")
    copper = _create_material_reference("copper")
    gold = _create_material_reference("gold")

    editor = _create_editor(references=[iron, copper, gold])
    crafting_materials = _get_crafting_materials(editor)

    crafting_materials._add_button.click()

    first_editor = crafting_materials.item_at(0)
    assert isinstance(first_editor, MaterialRequirementEditorWidget)

    first_field = _get_material_field(first_editor)
    first_field.setCurrentIndex(first_field.find_data_equal(copper))

    crafting_materials._add_button.click()

    second_editor = crafting_materials.item_at(1)
    assert isinstance(second_editor, MaterialRequirementEditorWidget)

    choices = _get_available_choices(_get_material_field(second_editor))

    assert iron in choices
    assert copper not in choices
    assert gold in choices


def test_currently_selected_material_remains_available(qapp: QApplication) -> None:
    """Keep the selected material available when refreshing choices."""
    iron = _create_material_reference("iron")
    copper = _create_material_reference("copper")
    gold = _create_material_reference("gold")

    editor = _create_editor(references=[iron, copper, gold])
    crafting_materials = _get_crafting_materials(editor)

    crafting_materials._add_button.click()

    requirement_editor = crafting_materials.item_at(0)
    assert isinstance(requirement_editor, MaterialRequirementEditorWidget)

    field = _get_material_field(requirement_editor)
    field.setCurrentIndex(field.find_data_equal(copper))

    choices = _get_available_choices(field)

    assert copper in choices
    assert iron in choices
    assert gold in choices


def test_removing_requirement_makes_its_material_available_again(qapp: QApplication) -> None:
    """Make a material available again after removing its requirement."""
    iron = _create_material_reference("iron")
    copper = _create_material_reference("copper")
    gold = _create_material_reference("gold")

    editor = _create_editor(references=[iron, copper, gold])
    crafting_materials = _get_crafting_materials(editor)

    crafting_materials._add_button.click()

    first_editor = crafting_materials.item_at(0)
    assert isinstance(first_editor, MaterialRequirementEditorWidget)

    first_field = _get_material_field(first_editor)
    first_field.setCurrentIndex(first_field.find_data_equal(copper))

    crafting_materials._add_button.click()

    second_editor = crafting_materials.item_at(1)
    assert isinstance(second_editor, MaterialRequirementEditorWidget)

    second_field = _get_material_field(second_editor)

    assert copper not in _get_available_choices(second_field)

    crafting_materials._remove_buttons[0].click()

    assert crafting_materials.item_count() == 1

    choices = _get_available_choices(second_field)

    assert copper in choices
    assert iron in choices
    assert gold in choices


def test_refresh_enables_adding_requirements_when_materials_become_available(
    qapp: QApplication,
) -> None:
    """Enable adding requirements after the available materials change."""
    references: list[ContentReference] = []
    editor = _create_editor(references=references)
    crafting_materials = _get_crafting_materials(editor)

    assert not crafting_materials._add_button.isEnabled()

    references.append(_create_material_reference("copper"))
    editor.refresh()

    assert crafting_materials._add_button.isEnabled()


def test_refresh_disables_adding_requirements_when_no_materials_are_available(
    qapp: QApplication,
) -> None:
    """Disable adding requirements when no materials are available."""
    references = [_create_material_reference("copper")]
    editor = _create_editor(references=references)
    crafting_materials = _get_crafting_materials(editor)

    assert crafting_materials._add_button.isEnabled()

    references.clear()
    editor.refresh()

    assert not crafting_materials._add_button.isEnabled()
