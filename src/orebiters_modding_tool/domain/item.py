from dataclasses import dataclass, field
from typing import ClassVar

from orebiters_modding_tool.domain.content import Content, ContentLocalization, ContentType
from orebiters_modding_tool.domain.material import MaterialRequirement


@dataclass(slots=True, kw_only=True)
class ItemLocalization(ContentLocalization):
    """Localized item text."""

    hint: str = ""
    description: str = ""


@dataclass(kw_only=True)
class Item(Content[ItemLocalization]):
    """Editable item definition."""

    CONTENT_TYPE: ClassVar[ContentType] = ContentType.ITEMS

    localizations: dict[str, ItemLocalization] = field(default_factory=dict)

    max_stack_size: int | None = None
    base_price: int | None = None
    crafting_materials: list[MaterialRequirement] = field(default_factory=list)
