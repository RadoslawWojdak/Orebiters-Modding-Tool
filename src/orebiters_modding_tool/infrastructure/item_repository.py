from typing import Any

from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.item import Item
from orebiters_modding_tool.domain.material import MaterialRequirement
from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.infrastructure.content_repository import ContentRepository


class ItemRepository(ContentRepository[Item]):
    """Handle item persistence on the file system."""

    CONTENT_TYPE = ContentType.ITEMS

    def _serialize(self, project: Project, item: Item) -> dict[str, object]:
        """Serialize an item to JSON-compatible data.

        :param project: Project containing the item.
        :param item: Item to serialize.
        :returns: Serialized item data.
        """
        return {
            "id": item.get_qualified_id(project.qualified_id),
            "max_stack_size": item.max_stack_size,
            "base_price": item.base_price,
            "crafting_materials": {
                requirement.material_reference.qualified_id: requirement.amount
                for requirement in item.crafting_materials
            },
            "icon_tag": f"items:{item.id}",
        }

    def _deserialize(self, data: dict[str, Any]) -> Item:
        """Deserialize JSON data into an item.

        :param data: Serialized item data.
        :returns: Deserialized item.
        """
        qualified_id = data["id"]
        item_id = qualified_id.rsplit(".", maxsplit=1)[1]

        crafting_materials_data = data.get("crafting_materials", {})

        crafting_materials = [
            MaterialRequirement(
                material_reference=ContentReference(
                    content_type=ContentType.MATERIALS,
                    qualified_id=material_qualified_id,
                ),
                amount=amount,
            )
            for material_qualified_id, amount in crafting_materials_data.items()
        ]

        return Item(
            id=item_id,
            localizations={},
            max_stack_size=data.get("max_stack_size"),
            base_price=data.get("base_price"),
            crafting_materials=crafting_materials,
        )
