from orebiters_modding_tool.app.models.column import Column
from orebiters_modding_tool.app.models.content_table_model import ContentTableModel
from orebiters_modding_tool.domain.content import ContentType
from orebiters_modding_tool.domain.item import Item


class ItemTableModel(ContentTableModel[Item]):
    """Table model for items."""

    CONTENT_TYPE = ContentType.ITEMS

    COLUMNS = (
        Column[Item](
            header="ID",
            tooltip="ID of the item",
            getter=lambda item: item.id,
        ),
        Column[Item](
            header="Name",
            tooltip="Name of the item",
            getter=lambda item: item.localizations["en"].one,
        ),
        Column[Item](
            header="Max. Stack Size",
            tooltip="Maximum stack size of the item in inventory",
            getter=lambda item: item.max_stack_size,
        ),
        Column[Item](
            header="Base Price",
            tooltip="Base price of the item",
            getter=lambda item: item.base_price,
        ),
        Column[Item](
            header="Craftable",
            tooltip="Whether the item can be crafted",
            getter=lambda item: "✔️" if bool(item.crafting_materials) else "",
            filterable=False,
        ),
    )
