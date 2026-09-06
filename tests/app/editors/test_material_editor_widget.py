import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from orebiters_modding_tool.app.editors.material_editor_widget import MaterialEditorWidget
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
            "material_references": [],
        },
    )

    qualified_id_field = editor._fields["qualified_id"]

    assert isinstance(qualified_id_field, QLabel)
    assert qualified_id_field.text() == "orebiters.core.iron"


def test_create_material_requirement_uses_first_material_reference(qapp: object) -> None:
    """Create a material requirement using the first available reference."""
    first_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.iron")
    second_reference = ContentReferenceFactory.create(qualified_id="orebiters.core.copper")

    requirement = MaterialEditorWidget._create_material_requirement(
        {
            "material_references": [first_reference, second_reference],
        },
    )

    assert isinstance(requirement, MaterialRequirement)
    assert requirement.material == first_reference
    assert requirement.amount == 1


def test_create_material_requirement_raises_without_material_references(
    self,
    qapp: object,
) -> None:
    """Raise an error when no material references are available."""
    with pytest.raises(
        ValueError,
        match="Cannot create a material requirement without material references.",
    ):
        MaterialEditorWidget._create_material_requirement({"material_references": []})


def test_read_only_makes_qualified_id_selectable(qapp: object) -> None:
    """Allow selecting the qualified ID in read-only mode."""
    material = MaterialFactory.create()

    editor = MaterialEditorWidget(
        material,
        context={
            "mod_id": "orebiters.core",
            "material_references": [],
        },
        read_only=True,
    )

    qualified_id_field = editor._fields["qualified_id"]

    assert isinstance(qualified_id_field, QLabel)
    assert qualified_id_field.textInteractionFlags() == Qt.TextInteractionFlag.TextSelectableByMouse
