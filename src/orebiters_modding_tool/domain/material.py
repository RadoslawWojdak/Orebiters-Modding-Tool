from dataclasses import dataclass, field
from typing import ClassVar

from orebiters_modding_tool.domain.content import (
    Content,
    ContentLocalization,
    ContentReference,
    ContentType,
)


@dataclass(slots=True, kw_only=True)
class MaterialLocalization(ContentLocalization):
    """Localized material text."""

    hint: str = ""
    description: str = ""


@dataclass(slots=True)
class MaterialRequirement:
    """Material required for crafting."""

    material: ContentReference
    amount: int


@dataclass(slots=True, kw_only=True)
class Material(Content[MaterialLocalization]):
    """Editable material definition."""

    CONTENT_TYPE: ClassVar[ContentType] = ContentType.MATERIALS

    localizations: dict[str, MaterialLocalization] = field(default_factory=dict)
    crafting_materials: list[MaterialRequirement] = field(default_factory=list)
