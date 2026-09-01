from pathlib import Path

from orebiters_modding_tool.domain.material import MaterialRequirement
from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.infrastructure.material_repository import MaterialRepository
from tests.factories.content import ContentReferenceFactory
from tests.factories.material import MaterialFactory


def test_save_and_load_material(tmp_path: Path) -> None:
    """Verify that a material can be saved and loaded."""
    repository = MaterialRepository(tmp_path)

    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    clay = MaterialFactory.create(id="clay")

    mud_patch_mix = MaterialFactory.create(
        id="mud_patch_mix",
        crafting_materials=[
            MaterialRequirement(
                material=ContentReferenceFactory.from_content(clay, mod_id=project.qualified_id),
                amount=2,
            ),
        ],
    )

    repository.save(project, mud_patch_mix)

    loaded_material = repository.load(project, mud_patch_mix.id)

    assert loaded_material.id == mud_patch_mix.id
    assert loaded_material.localizations == {}

    assert len(loaded_material.crafting_materials) == 1

    requirement = loaded_material.crafting_materials[0]

    assert requirement.material == ContentReferenceFactory.from_content(
        clay,
        mod_id=project.qualified_id,
    )
    assert requirement.amount == 2


def test_load_all_loads_all_materials(tmp_path: Path) -> None:
    """Verify that all project materials can be loaded."""
    repository = MaterialRepository(tmp_path)

    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    first_material = MaterialFactory.create(id="first_material")
    second_material = MaterialFactory.create(id="second_material")

    repository.save(project, first_material)
    repository.save(project, second_material)

    loaded_materials = repository.load_all(project)

    assert [material.id for material in loaded_materials] == ["first_material", "second_material"]
