from orebiters_modding_tool.domain.content import ContentLocalization, ContentState
from orebiters_modding_tool.domain.mineable import Drop, Mineable, MineableType


class MineableFactory:
    """Create mineables for tests."""

    _counter = 0

    @classmethod
    def create(
        cls,
        *,
        id: str | None = None,
        localizations: dict[str, ContentLocalization] | None = None,
        type: MineableType = MineableType.RESOURCE,
        tier: int | None = 1,
        value: int | None = 10,
        hardness: int = 5,
        min_drill_power: int = 2,
        min_depth: int | None = 10,
        max_depth: int | None = 100,
        peak_depth: int | None = 50,
        start_weight: float | None = None,
        end_weight: float | None = None,
        rarity: float | None = None,
        drops: list[Drop] | None = None,
        particle_colors: list[str] | None = None,
        damage_multiplier: float = 1.0,
        player_only_destruction: bool = False,
        state: ContentState = ContentState.SAVED,
    ) -> Mineable:
        """Create a mineable."""
        if id is None:
            cls._counter += 1
            id = f"mineable_{cls._counter}"

        if localizations is None:
            localizations = {
                "en": ContentLocalization(
                    one=id.replace("_", " ").title(),
                    few=id.replace("_", " ").title(),
                    many=id.replace("_", " ").title(),
                ),
            }

        if drops is None:
            drops = []

        if particle_colors is None:
            particle_colors = []

        return Mineable(
            id=id,
            localizations=localizations,
            state=state,
            type=type,
            tier=tier,
            value=value,
            hardness=hardness,
            min_drill_power=min_drill_power,
            min_depth=min_depth,
            max_depth=max_depth,
            peak_depth=peak_depth,
            start_weight=start_weight,
            end_weight=end_weight,
            rarity=rarity,
            drops=drops,
            particle_colors=particle_colors,
            damage_multiplier=damage_multiplier,
            player_only_destruction=player_only_destruction,
        )
