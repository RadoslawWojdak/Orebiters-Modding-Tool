from collections.abc import Callable
from typing import Any

from orebiters_modding_tool.domain.content import Content, ContentState, ContentType
from orebiters_modding_tool.domain.material import Material, MaterialLocalization

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
}
