from dataclasses import dataclass, field
from typing import Any

from orebiters_modding_tool.domain.content import Content, ContentType
from orebiters_modding_tool.domain.project_identifier import create_qualified_id


@dataclass(slots=True, kw_only=True)
class Project:
    """Editable mod project."""

    namespace: str
    mod_id: str
    name: str
    content: dict[ContentType, list[Content[Any]]] = field(
        default_factory=lambda: {content_type: [] for content_type in ContentType}
    )

    @property
    def qualified_id(self) -> str:
        """Return the globally qualified mod identifier.

        :returns: Qualified mod ID.
        """
        return create_qualified_id(self.namespace, self.mod_id)
