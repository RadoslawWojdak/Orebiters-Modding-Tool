import json
from pathlib import Path

import pytest

from orebiters_modding_tool.domain.content import ContentType
from orebiters_modding_tool.domain.mineable import MineableType
from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.infrastructure.mineable_repository import MineableRepository
from tests.factories.content import ContentReferenceFactory
from tests.factories.drop import DropFactory
from tests.factories.mineable import MineableFactory


@pytest.fixture
def repository(tmp_path: Path) -> MineableRepository:
    """Create a mineable repository using a temporary directory."""
    return MineableRepository(tmp_path)


def test_save_and_load_mineable(repository: MineableRepository, project: Project) -> None:
    """Verify that a mineable can be saved and loaded."""
    iron = ContentReferenceFactory.create(
        content_type=ContentType.MATERIALS,
        qualified_id=f"{project.qualified_id}.iron",
    )

    mineable = MineableFactory.create(
        id="iron_ore",
        type=MineableType.RESOURCE,
        tier=2,
        value=25,
        hardness=8,
        min_drill_power=4,
        min_depth=10,
        max_depth=100,
        peak_depth=50,
        drops=[DropFactory.create(item=iron, probability=0.75)],
        particle_colors=["#FF0000", "#00FF00"],
        damage_multiplier=1.5,
        player_only_destruction=True,
    )

    repository.save(project, mineable)

    loaded_mineable = repository.load(project, mineable.id)

    assert loaded_mineable.id == mineable.id
    assert loaded_mineable.localizations == {}
    assert loaded_mineable.type == MineableType.RESOURCE
    assert loaded_mineable.tier == 2
    assert loaded_mineable.value == 25
    assert loaded_mineable.hardness == 8
    assert loaded_mineable.min_drill_power == 4
    assert loaded_mineable.min_depth == 10
    assert loaded_mineable.max_depth == 100
    assert loaded_mineable.peak_depth == 50
    assert loaded_mineable.drops == [DropFactory.create(item=iron, probability=0.75)]
    assert loaded_mineable.particle_colors == ["#FF0000", "#00FF00"]
    assert loaded_mineable.damage_multiplier == 1.5
    assert loaded_mineable.player_only_destruction is True


@pytest.mark.parametrize(
    ("mineable_type", "expected_icon_tag"),
    [
        (MineableType.RESOURCE, "mineables:iron_ore"),
        (MineableType.ARTIFACT, "mineables:ancient_artifact"),
    ],
)
def test_save_mineable_writes_icon_tag(
    repository: MineableRepository,
    project: Project,
    mineable_type: MineableType,
    expected_icon_tag: str,
) -> None:
    """Persist an icon tag for mineable types that have an icon."""
    mineable_id = expected_icon_tag.removeprefix("mineables:")

    repository.save(project, MineableFactory.create(id=mineable_id, type=mineable_type))

    file_path = (
        repository._mods_directory
        / project.qualified_id
        / ContentType.MINEABLES.value
        / f"{mineable_id}.json"
    )

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["icon_tag"] == expected_icon_tag


def test_save_mineable_without_icon_tag_for_obstacle(
    repository: MineableRepository,
    project: Project,
) -> None:
    """Do not persist an icon tag for obstacles."""
    repository.save(project, MineableFactory.create(id="spike", type=MineableType.OBSTACLE))

    file_path = (
        repository._mods_directory
        / project.qualified_id
        / ContentType.MINEABLES.value
        / "spike.json"
    )

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert "icon_tag" not in data


def test_serialize_mineable(project: Project, repository: MineableRepository) -> None:
    """Serialize a mineable into the expected JSON structure."""
    mineable = MineableFactory.create(
        id="iron_ore",
        type=MineableType.RESOURCE,
        tier=2,
        value=25,
        hardness=8,
        min_drill_power=4,
        min_depth=10,
        max_depth=100,
        peak_depth=50,
        drops=[],
        particle_colors=["#FF0000"],
    )

    data = repository._serialize(project, mineable)

    assert data == {
        "id": mineable.get_qualified_id(project.qualified_id),
        "type": "resource",
        "tier": 2,
        "value": 25,
        "hardness": 8,
        "min_drill_power": 4,
        "min_depth": 10,
        "max_depth": 100,
        "peak_depth": 50,
        "drops": {},
        "particle_colors": ["#FF0000"],
        "icon_tag": "mineables:iron_ore",
    }


def test_serialize_mineable_with_drops(project: Project, repository: MineableRepository) -> None:
    """Serialize drop references and their probabilities."""
    mineable = MineableFactory.create(
        drops=[
            DropFactory.create(
                item=ContentReferenceFactory.create(
                    content_type=ContentType.MATERIALS,
                    qualified_id=f"{project.qualified_id}.iron",
                ),
                probability=0.75,
            ),
            DropFactory.create(
                item=ContentReferenceFactory.create(
                    content_type=ContentType.MATERIALS,
                    qualified_id=f"{project.qualified_id}.coal",
                ),
                probability=0.25,
            ),
        ],
    )

    data = repository._serialize(project, mineable)

    assert data["drops"] == {
        f"{project.qualified_id}.iron": 0.75,
        f"{project.qualified_id}.coal": 0.25,
    }


def test_serialize_mineable_with_generation_fields(
    project: Project,
    repository: MineableRepository,
) -> None:
    """Serialize populated generation fields."""
    mineable = MineableFactory.create(
        start_weight=0.2,
        end_weight=0.8,
        peak_depth=None,
        rarity=0.15,
    )

    data = repository._serialize(project, mineable)

    assert data["start_weight"] == 0.2
    assert data["end_weight"] == 0.8
    assert "peak_depth" not in data
    assert data["rarity"] == 0.15


def test_serialize_mineable_with_non_default_optional_properties(
    project: Project,
    repository: MineableRepository,
) -> None:
    """Serialize optional properties when they differ from their defaults."""
    mineable = MineableFactory.create(
        damage_multiplier=1.5,
        player_only_destruction=True,
    )

    data = repository._serialize(project, mineable)

    assert data["damage_multiplier"] == 1.5
    assert data["player_only_destruction"] is True


def test_serialize_mineable_omits_default_optional_properties(
    project: Project,
    repository: MineableRepository,
) -> None:
    """Omit optional properties when they have their default values."""
    mineable = MineableFactory.create(
        value=None,
        damage_multiplier=1.0,
        player_only_destruction=False,
    )

    data = repository._serialize(project, mineable)

    assert "value" not in data
    assert "damage_multiplier" not in data
    assert "player_only_destruction" not in data


def test_deserialize_mineable(repository: MineableRepository) -> None:
    """Deserialize a mineable with no optional collections."""
    mineable = repository._deserialize(
        {
            "id": "example.iron_ore",
            "type": "resource",
            "hardness": 8,
            "min_drill_power": 4,
            "min_depth": 10,
            "max_depth": 100,
            "drops": {},
            "particle_colors": [],
        }
    )

    assert mineable.id == "iron_ore"
    assert mineable.localizations == {}
    assert mineable.type == MineableType.RESOURCE
    assert mineable.tier is None
    assert mineable.value is None
    assert mineable.hardness == 8
    assert mineable.min_drill_power == 4
    assert mineable.min_depth == 10
    assert mineable.max_depth == 100
    assert mineable.start_weight is None
    assert mineable.end_weight is None
    assert mineable.peak_depth is None
    assert mineable.rarity is None
    assert mineable.drops == []
    assert mineable.particle_colors == []
    assert mineable.damage_multiplier == 1.0
    assert mineable.player_only_destruction is False


def test_deserialize_mineable_without_optional_fields(repository: MineableRepository) -> None:
    """Use defaults when optional fields are absent."""
    mineable = repository._deserialize(
        {
            "id": "example.iron_ore",
            "type": "resource",
            "hardness": 8,
            "min_drill_power": 4,
            "min_depth": 10,
            "max_depth": 100,
        }
    )

    assert mineable.tier is None
    assert mineable.value is None
    assert mineable.drops == []
    assert mineable.particle_colors == []
    assert mineable.damage_multiplier == 1.0
    assert mineable.player_only_destruction is False


def test_deserialize_mineable_with_generation_fields(repository: MineableRepository) -> None:
    """Deserialize generation fields."""
    mineable = repository._deserialize(
        {
            "id": "example.iron_ore",
            "type": "resource",
            "hardness": 8,
            "min_drill_power": 4,
            "min_depth": 10,
            "max_depth": 100,
            "start_weight": 0.2,
            "end_weight": 0.8,
            "peak_depth": 50,
            "rarity": 0.15,
        }
    )

    assert mineable.start_weight == 0.2
    assert mineable.end_weight == 0.8
    assert mineable.peak_depth == 50
    assert mineable.rarity == 0.15


def test_deserialize_mineable_with_drops(repository: MineableRepository) -> None:
    """Deserialize drop references and probabilities."""
    mineable = repository._deserialize(
        {
            "id": "example.iron_ore",
            "type": "resource",
            "hardness": 8,
            "min_drill_power": 4,
            "min_depth": 10,
            "max_depth": 100,
            "drops": {
                "example.iron": 0.75,
                "example.coal": 0.25,
            },
        }
    )

    assert len(mineable.drops) == 2

    drops = {drop.item.qualified_id: drop.probability for drop in mineable.drops}

    assert drops == {
        "example.iron": 0.75,
        "example.coal": 0.25,
    }

    assert all(drop.item.content_type == ContentType.MATERIALS for drop in mineable.drops)


def test_deserialize_mineable_with_optional_properties(repository: MineableRepository) -> None:
    """Deserialize optional properties."""
    mineable = repository._deserialize(
        {
            "id": "example.iron_ore",
            "type": "resource",
            "hardness": 8,
            "min_drill_power": 4,
            "min_depth": 10,
            "max_depth": 100,
            "value": 25,
            "damage_multiplier": 1.5,
            "player_only_destruction": True,
            "particle_colors": ["#FF0000", "#00FF00"],
        }
    )

    assert mineable.value == 25
    assert mineable.damage_multiplier == 1.5
    assert mineable.player_only_destruction is True
    assert mineable.particle_colors == ["#FF0000", "#00FF00"]


@pytest.mark.parametrize(
    ("qualified_id", "expected_id"),
    [
        ("example.iron_ore", "iron_ore"),
        ("my.mod.iron_ore", "iron_ore"),
    ],
)
def test_deserialize_extracts_local_id(
    qualified_id: str,
    expected_id: str,
    repository: MineableRepository,
) -> None:
    """Extract the local ID from the last segment of a qualified ID."""
    mineable = repository._deserialize(
        {
            "id": qualified_id,
            "type": "resource",
            "hardness": 8,
            "min_drill_power": 4,
            "min_depth": 10,
            "max_depth": 100,
        }
    )

    assert mineable.id == expected_id
