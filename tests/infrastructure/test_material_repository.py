from pathlib import Path

from orebiters_modding_tool.domain.content import ContentReference, ContentType
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


def test_load_all_returns_empty_list_when_materials_directory_does_not_exist(
    tmp_path: Path,
) -> None:
    """Return an empty list when the materials directory does not exist."""
    repository = MaterialRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    assert repository.load_all(project) == []


def test_list_material_ids_returns_sorted_ids(tmp_path: Path) -> None:
    """Return material IDs in sorted order."""
    repository = MaterialRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    repository.save(project, MaterialFactory.create(id="stone"))
    repository.save(project, MaterialFactory.create(id="clay"))
    repository.save(project, MaterialFactory.create(id="copper"))

    assert repository.list_material_ids(project) == ["clay", "copper", "stone"]


def test_list_material_ids_returns_empty_list_when_materials_directory_does_not_exist(
    tmp_path: Path,
) -> None:
    """Return an empty list when the materials directory does not exist."""
    repository = MaterialRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    assert repository.list_material_ids(project) == []


def test_delete_removes_material(tmp_path: Path) -> None:
    """Remove a material from the project."""
    repository = MaterialRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    material = MaterialFactory.create(id="clay")
    repository.save(project, material)

    repository.delete(project, material.id)

    assert repository.list_material_ids(project) == []


def test_save_overwrites_existing_material(tmp_path: Path) -> None:
    """Overwrite an existing material when saving it again."""
    repository = MaterialRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    material = MaterialFactory.create(id="clay")
    repository.save(project, material)

    material.crafting_materials.append(
        MaterialRequirement(
            material=ContentReference(
                content_type=ContentType.MATERIALS,
                qualified_id="test.test_mod.stone",
            ),
            amount=2,
        ),
    )

    repository.save(project, material)

    loaded_material = repository.load(project, material.id)

    assert loaded_material.crafting_materials == material.crafting_materials
