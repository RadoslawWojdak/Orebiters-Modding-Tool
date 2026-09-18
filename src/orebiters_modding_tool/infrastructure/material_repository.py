from typing import Any

from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.material import Material, MaterialRequirement
from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.infrastructure.content_repository import ContentRepository


class MaterialRepository(ContentRepository[Material]):
    """Handle material persistence on the file system."""

    CONTENT_TYPE = ContentType.MATERIALS

    def _serialize(self, project: Project, material: Material) -> dict[str, object]:
        """Serialize a material to JSON-compatible data.

        :param project: Project containing the material.
        :param material: Material to serialize.
        :returns: Serialized material data.
        """
        return {
            "id": material.get_qualified_id(project.qualified_id),
            "icon_tag": f"materials:{material.id}",
            "crafting_materials": {
                requirement.material_reference.qualified_id: requirement.amount
                for requirement in material.crafting_materials
            },
        }

    def _deserialize(self, data: dict[str, Any]) -> Material:
        """Deserialize JSON data into a material.

        :param data: Serialized material data.
        :returns: Deserialized material.
        """
        qualified_id = data["id"]
        material_id = qualified_id.rsplit(".", maxsplit=1)[1]

        crafting_materials_data = data.get("crafting_materials", {})

        crafting_materials = [
            MaterialRequirement(
                material_reference=ContentReference(
                    content_type=ContentType.MATERIALS,
                    qualified_id=qualified_id,
                ),
                amount=amount,
            )
            for qualified_id, amount in crafting_materials_data.items()
        ]

        return Material(id=material_id, localizations={}, crafting_materials=crafting_materials)
