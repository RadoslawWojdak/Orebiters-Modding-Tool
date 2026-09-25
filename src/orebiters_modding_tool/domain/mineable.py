from dataclasses import dataclass, field
from typing import ClassVar

from orebiters_modding_tool.domain.content import (
    Content,
    ContentLocalization,
    ContentReference,
    ContentType,
)
from orebiters_modding_tool.domain.enums import DisplayEnum


class MineableType(DisplayEnum):
    """Type of mineable."""

    RESOURCE = ("resource", "Resources", "Resource")
    OBSTACLE = ("obstacle", "Obstacles", "Obstacle")
    ARTIFACT = ("artifact", "Artifacts", "Artifact")


@dataclass(slots=True)
class Drop:
    """Item that can be dropped by a content entity."""

    item: ContentReference
    probability: float


@dataclass(kw_only=True)
class Mineable(Content[ContentLocalization]):
    """Editable mineable definition."""

    CONTENT_TYPE: ClassVar[ContentType] = ContentType.MINEABLES

    type: MineableType
    tier: int | None = None
    value: int | None = None

    hardness: int
    min_drill_power: int
    min_depth: int | None
    max_depth: int | None

    peak_depth: int | None = None
    start_weight: float | None = None
    end_weight: float | None = None
    rarity: float | None = None

    drops: list[Drop] = field(default_factory=list)
    particle_colors: list[str] = field(default_factory=list)

    damage_multiplier: float = 1.0
    player_only_destruction: bool = False
