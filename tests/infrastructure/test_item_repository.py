import json
from pathlib import Path

import pytest

from orebiters_modding_tool.domain.content import ContentType
from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.infrastructure.item_repository import ItemRepository
from tests.factories.content_factory import ContentReferenceFactory
from tests.factories.item_factory import ItemFactory
from tests.factories.material_factory import MaterialFactory
from tests.factories.material_requirement_factory import MaterialRequirementFactory


@pytest.fixture
def repository(tmp_path: Path) -> ItemRepository:
    """Create an item repository using a temporary directory."""
    return ItemRepository(tmp_path)


def test_save_and_load_item(repository: ItemRepository, project: Project) -> None:
    """Verify that an item can be saved and loaded."""
    clay = MaterialFactory.create(id="clay")

    fuel_canister = ItemFactory.create(
        id="fuel_canister",
        max_stack_size=1,
        base_price=100,
        crafting_materials=[
            MaterialRequirementFactory.create(
                ContentReferenceFactory.from_content(clay, mod_id=project.qualified_id),
                amount=2,
            ),
        ],
    )

    repository.save(project, fuel_canister)

    loaded_item = repository.load(project, fuel_canister.id)

    assert loaded_item.id == fuel_canister.id
    assert loaded_item.localizations == {}
    assert loaded_item.max_stack_size == 1
    assert loaded_item.base_price == 100

    assert len(loaded_item.crafting_materials) == 1

    requirement = loaded_item.crafting_materials[0]

    assert requirement.material_reference == ContentReferenceFactory.from_content(
        clay,
        mod_id=project.qualified_id,
    )
    assert requirement.amount == 2


def test_save_item_writes_icon_tag(repository: ItemRepository, project: Project) -> None:
    """Persist the item icon tag using its local ID."""
    repository.save(project, ItemFactory.create(id="fuel_canister"))

    file_path = (
        repository._mods_directory
        / project.qualified_id
        / ContentType.ITEMS.value
        / "fuel_canister.json"
    )

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["icon_tag"] == "items:fuel_canister"


def test_serialize_item(project: Project, repository: ItemRepository) -> None:
    """Serialize an item into the expected JSON structure."""
    item = ItemFactory.create(
        id="fuel_canister",
        max_stack_size=1,
        base_price=100,
        crafting_materials=[],
    )

    data = repository._serialize(project, item)

    assert data == {
        "id": item.get_qualified_id(project.qualified_id),
        "max_stack_size": 1,
        "base_price": 100,
        "crafting_materials": {},
        "icon_tag": "items:fuel_canister",
    }


def test_serialize_item_with_crafting_materials(
    project: Project,
    repository: ItemRepository,
) -> None:
    """Serialize crafting material references and their amounts."""
    item = ItemFactory.create(
        id="fuel_canister",
        crafting_materials=[
            MaterialRequirementFactory.create(
                ContentReferenceFactory.create(f"{project.qualified_id}.materials.clay"),
                amount=3,
            ),
            MaterialRequirementFactory.create(
                ContentReferenceFactory.create(f"{project.qualified_id}.materials.coal_resin"),
                amount=2,
            ),
        ],
    )

    data = repository._serialize(project, item)

    assert data["crafting_materials"] == {
        f"{project.qualified_id}.materials.clay": 3,
        f"{project.qualified_id}.materials.coal_resin": 2,
    }


def test_deserialize_item(repository: ItemRepository) -> None:
    """Deserialize an item with no crafting materials."""
    item = repository._deserialize(
        {
            "id": "orebiters.core.items.fuel_canister",
            "max_stack_size": 1,
            "base_price": 100,
            "crafting_materials": {},
        }
    )

    assert item.id == "fuel_canister"
    assert item.localizations == {}
    assert item.max_stack_size == 1
    assert item.base_price == 100
    assert item.crafting_materials == []


def test_deserialize_item_without_optional_fields(repository: ItemRepository) -> None:
    """Allow optional item fields to be absent."""
    item = repository._deserialize({"id": "orebiters.core.items.fuel_canister"})

    assert item.id == "fuel_canister"
    assert item.max_stack_size is None
    assert item.base_price is None
    assert item.crafting_materials == []


def test_deserialize_item_with_crafting_materials(repository: ItemRepository) -> None:
    """Deserialize crafting material references and amounts."""
    item = repository._deserialize(
        {
            "id": "orebiters.core.items.fuel_canister",
            "max_stack_size": 1,
            "base_price": 100,
            "crafting_materials": {
                "orebiters.core.materials.clay": 3,
                "orebiters.core.materials.coal_resin": 2,
            },
        }
    )

    assert item.id == "fuel_canister"
    assert len(item.crafting_materials) == 2

    requirements = {
        requirement.material_reference.qualified_id: requirement.amount
        for requirement in item.crafting_materials
    }

    assert requirements == {
        "orebiters.core.materials.clay": 3,
        "orebiters.core.materials.coal_resin": 2,
    }

    assert all(
        requirement.material_reference.content_type == ContentType.MATERIALS
        for requirement in item.crafting_materials
    )


@pytest.mark.parametrize(
    ("qualified_id", "expected_id"),
    [
        ("orebiters.core.items.fuel_canister", "fuel_canister"),
        ("my.mod.items.fuel_canister", "fuel_canister"),
    ],
)
def test_deserialize_extracts_local_id(
    qualified_id: str,
    expected_id: str,
    repository: ItemRepository,
) -> None:
    """Extract the local ID from the last segment of a qualified ID."""
    item = repository._deserialize(
        {
            "id": qualified_id,
            "crafting_materials": {},
        }
    )

    assert item.id == expected_id
