from collections.abc import Callable
from typing import Any

from orebiters_modding_tool.domain import Mineable
from orebiters_modding_tool.domain.content import (
    Content,
    ContentLocalization,
    ContentState,
    ContentType,
)
from orebiters_modding_tool.domain.material import Material, MaterialLocalization
from orebiters_modding_tool.domain.mineable import MineableType

ContentFactory = Callable[[str], Content[Any]]


CONTENT_FACTORY_REGISTRY: dict[ContentType, ContentFactory] = {
    ContentType.MATERIALS: lambda content_id: Material(
        id=content_id,
        localizations={
            "en": MaterialLocalization(),
            "pl": MaterialLocalization(),
        },
        crafting_materials=[],
        state=ContentState.NEW,
    ),
    ContentType.MINEABLES: lambda content_id: Mineable(
        id=content_id,
        localizations={
            "en": ContentLocalization(),
            "pl": ContentLocalization(),
        },
        type=MineableType.RESOURCE,
        hardness=1,
        min_drill_power=1,
        min_depth=None,
        max_depth=None,
        state=ContentState.NEW,
    ),
}
