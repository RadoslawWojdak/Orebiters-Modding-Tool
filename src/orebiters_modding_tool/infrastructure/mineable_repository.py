from typing import Any

from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.mineable import Drop, Mineable, MineableType
from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.infrastructure.content_repository import ContentRepository


class MineableRepository(ContentRepository[Mineable]):
    """Handle mineable persistence on the file system."""

    CONTENT_TYPE = ContentType.MINEABLES

    def _serialize(self, project: Project, mineable: Mineable) -> dict[str, object]:
        """Serialize a mineable to JSON-compatible data.

        :param project: Project containing the mineable.
        :param mineable: Mineable to serialize.
        :returns: Serialized mineable data.
        """
        data: dict[str, object] = {
            "id": mineable.get_qualified_id(project.qualified_id),
            "type": mineable.type.value,
            "tier": mineable.tier,
        }

        if mineable.value is not None:
            data["value"] = mineable.value

        data |= {
            "hardness": mineable.hardness,
            "min_drill_power": mineable.min_drill_power,
            "min_depth": mineable.min_depth,
            "max_depth": mineable.max_depth,
        }

        generation_fields = ("start_weight", "end_weight", "peak_depth", "rarity")
        for field_name in generation_fields:
            value = getattr(mineable, field_name)
            if value is not None:
                data[field_name] = value

        data |= {
            "drops": {drop.item.qualified_id: drop.probability for drop in mineable.drops},
            "particle_colors": mineable.particle_colors,
        }

        if mineable.damage_multiplier != 1.0:
            data["damage_multiplier"] = mineable.damage_multiplier

        if mineable.player_only_destruction:
            data["player_only_destruction"] = mineable.player_only_destruction

        if mineable.type in (MineableType.RESOURCE, MineableType.ARTIFACT):
            data["icon_tag"] = f"mineables:{mineable.id}"

        return data

    def _deserialize(self, data: dict[str, Any]) -> Mineable:
        """Deserialize JSON data into a mineable.

        :param data: Serialized mineable data.
        :returns: Deserialized mineable.
        """
        qualified_id = data["id"]
        mineable_id = qualified_id.rsplit(".", maxsplit=1)[1]

        drops_data = data.get("drops", {})

        drops = [
            Drop(
                item=ContentReference(
                    content_type=ContentType.MATERIALS,
                    qualified_id=qualified_id,
                ),
                probability=probability,
            )
            for qualified_id, probability in drops_data.items()
        ]

        return Mineable(
            id=mineable_id,
            localizations={},
            type=MineableType(data["type"]),  # type: ignore[call-arg]
            tier=data.get("tier"),
            value=data.get("value"),
            hardness=data["hardness"],
            min_drill_power=data["min_drill_power"],
            min_depth=data.get("min_depth"),
            max_depth=data.get("max_depth"),
            start_weight=data.get("start_weight"),
            end_weight=data.get("end_weight"),
            peak_depth=data.get("peak_depth"),
            rarity=data.get("rarity"),
            drops=drops,
            particle_colors=data.get("particle_colors", []),
            damage_multiplier=data.get("damage_multiplier", 1.0),
            player_only_destruction=data.get("player_only_destruction", False),
        )
