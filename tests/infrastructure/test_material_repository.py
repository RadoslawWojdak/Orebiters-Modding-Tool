import json
from pathlib import Path

import pytest

from orebiters_modding_tool.domain.content import ContentType
from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.infrastructure.material_repository import MaterialRepository
from tests.factories.content import ContentReferenceFactory
from tests.factories.material import MaterialFactory
from tests.factories.material_requirement import MaterialRequirementFactory


@pytest.fixture
def repository(tmp_path: Path) -> MaterialRepository:
    """Create a material repository using a temporary directory."""
    return MaterialRepository(tmp_path)


def test_save_and_load_material(repository: MaterialRepository, project: Project) -> None:
    """Verify that a material can be saved and loaded."""
    clay = MaterialFactory.create(id="clay")

    mud_patch_mix = MaterialFactory.create(
        id="mud_patch_mix",
        crafting_materials=[
            MaterialRequirementFactory.create(
                ContentReferenceFactory.from_content(clay, mod_id=project.qualified_id),
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

    assert requirement.material_reference == ContentReferenceFactory.from_content(
        clay,
        mod_id=project.qualified_id,
    )
    assert requirement.amount == 2


def test_save_material_writes_icon_tag(repository: MaterialRepository, project: Project) -> None:
    """Persist the material icon tag using its local ID."""
    repository.save(project, MaterialFactory.create(id="iron"))

    file_path = (
        repository._mods_directory
        / project.qualified_id
        / ContentType.MATERIALS.value
        / "iron.json"
    )

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["icon_tag"] == "materials:iron"


def test_serialize_material(project: Project, repository: MaterialRepository) -> None:
    """Serialize a material into the expected JSON structure."""
    material = MaterialFactory.create(id="iron", crafting_materials=[])

    data = repository._serialize(project, material)

    assert data == {
        "id": material.get_qualified_id(project.qualified_id),
        "icon_tag": "materials:iron",
        "crafting_materials": {},
    }


def test_serialize_material_with_crafting_materials(
    project: Project,
    repository: MaterialRepository,
) -> None:
    """Serialize crafting material references and their amounts."""
    material = MaterialFactory.create(
        crafting_materials=[
            MaterialRequirementFactory.create(
                material_reference=ContentReferenceFactory.create(
                    content_type=ContentType.MATERIALS,
                    qualified_id=f"{project.qualified_id}.iron",
                ),
                amount=3,
            ),
            MaterialRequirementFactory.create(
                material_reference=ContentReferenceFactory.create(
                    content_type=ContentType.MATERIALS,
                    qualified_id=f"{project.qualified_id}.coal",
                ),
                amount=2,
            ),
        ],
    )

    data = repository._serialize(project, material)

    assert data["crafting_materials"] == {
        f"{project.qualified_id}.iron": 3,
        f"{project.qualified_id}.coal": 2,
    }


def test_deserialize_material(repository: MaterialRepository) -> None:
    """Deserialize a material with no crafting materials."""
    material = repository._deserialize(
        {
            "id": "example.iron",
            "crafting_materials": {},
        }
    )

    assert material.id == "iron"
    assert material.localizations == {}
    assert material.crafting_materials == []


def test_deserialize_material_without_crafting_materials(repository: MaterialRepository) -> None:
    """Allow the crafting materials field to be absent."""
    material = repository._deserialize({"id": "example.iron"})

    assert material.id == "iron"
    assert material.crafting_materials == []


def test_deserialize_material_with_crafting_materials(repository: MaterialRepository) -> None:
    """Deserialize crafting material references and amounts."""
    material = repository._deserialize(
        {
            "id": "example.steel",
            "crafting_materials": {
                "example.iron": 3,
                "example.coal": 2,
            },
        }
    )

    assert material.id == "steel"
    assert len(material.crafting_materials) == 2

    requirements = {
        requirement.material_reference.qualified_id: requirement.amount
        for requirement in material.crafting_materials
    }

    assert requirements == {
        "example.iron": 3,
        "example.coal": 2,
    }

    assert all(
        requirement.material_reference.content_type == ContentType.MATERIALS
        for requirement in material.crafting_materials
    )


@pytest.mark.parametrize(
    ("qualified_id", "expected_id"),
    [
        ("example.iron", "iron"),
        ("my.mod.iron", "iron"),
    ],
)
def test_deserialize_extracts_local_id(
    qualified_id: str,
    expected_id: str,
    repository: MaterialRepository,
) -> None:
    """Extract the local ID from the last segment of a qualified ID."""
    material = repository._deserialize(
        {
            "id": qualified_id,
            "crafting_materials": {},
        }
    )

    assert material.id == expected_id
