from orebiters_modding_tool.app.models.column import Column
from orebiters_modding_tool.app.models.content_table_model import ContentTableModel
from orebiters_modding_tool.domain.material import Material


class MaterialTableModel(ContentTableModel[Material]):
    """Table model for materials."""

    COLUMNS = (
        Column[Material](
            header="ID",
            tooltip="ID of the material",
            getter=lambda material: material.id,
        ),
        Column[Material](
            header="Name",
            tooltip="Name of the material",
            getter=lambda material: material.localizations["en"].one,
        ),
        Column[Material](
            header="Hint",
            tooltip="Short description of the material",
            getter=lambda material: material.localizations["en"].hint,
        ),
        Column[Material](
            header="Craftable",
            tooltip="Whether the material can be crafted",
            getter=lambda material: "✔️" if bool(material.crafting_materials) else "",
            filterable=False,
        ),
    )
