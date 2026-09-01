from orebiters_modding_tool.domain.material import Material
from orebiters_modding_tool.models.base_table_model import BaseTableModel
from orebiters_modding_tool.models.column import Column


class MaterialTableModel(BaseTableModel[Material]):
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
        ),
    )
