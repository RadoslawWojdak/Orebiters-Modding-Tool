from dataclasses import dataclass, field

from orebiters_modding_tool.domain.material import Material
from orebiters_modding_tool.domain.project_identifier import create_qualified_id


@dataclass(slots=True, kw_only=True)
class Project:
    """Editable mod project."""

    namespace: str
    mod_id: str
    name: str
    materials: list[Material] = field(default_factory=list)

    @property
    def qualified_id(self) -> str:
        """Return the globally qualified mod identifier.

        :returns: Qualified mod ID.
        """
        return create_qualified_id(self.namespace, self.mod_id)
