from orebiters_modding_tool.app.models.column import Column
from orebiters_modding_tool.app.models.content_table_model import ContentTableModel
from orebiters_modding_tool.domain.content import ContentType
from orebiters_modding_tool.domain.mineable import Mineable


class MineableTableModel(ContentTableModel[Mineable]):
    """Table model for mineables."""

    CONTENT_TYPE = ContentType.MINEABLES

    COLUMNS = (
        Column[Mineable](
            header="ID",
            tooltip="ID of the mineable",
            getter=lambda mineable: mineable.id,
        ),
        Column[Mineable](
            header="Name",
            tooltip="Name of the mineable",
            getter=lambda mineable: mineable.localizations["en"].one,
        ),
        Column[Mineable](
            header="Type",
            tooltip="Type of the mineable",
            getter=lambda mineable: mineable.type.value,
        ),
        Column[Mineable](
            header="Tier",
            tooltip="Tier of the mineable",
            getter=lambda mineable: mineable.tier,
        ),
        Column[Mineable](
            header="Value",
            tooltip="Sale value of the mineable",
            getter=lambda mineable: mineable.value,
        ),
        Column[Mineable](
            header="Hardness",
            tooltip="Hardness of the mineable",
            getter=lambda mineable: mineable.hardness,
        ),
        Column[Mineable](
            header="Min. Drill Power",
            tooltip="Minimum drill power required to mine",
            getter=lambda mineable: mineable.min_drill_power,
        ),
        Column[Mineable](
            header="Depth",
            tooltip="Depth range where the mineable can appear",
            getter=lambda mineable: (
                f"{mineable.min_depth if mineable.min_depth is not None else '0'}"
                f" – "
                f"{mineable.max_depth if mineable.max_depth is not None else '∞'}"
            ),
            sorter=lambda mineable: (
                mineable.min_depth if mineable.min_depth is not None else 0,
                mineable.max_depth if mineable.max_depth is not None else float("inf"),
            ),
        ),
    )
