from dataclasses import dataclass

from orebiters_modding_tool.app.models.base_table_model import BaseTableModel
from orebiters_modding_tool.app.models.column import Column


@dataclass
class ItemSample:
    """Sample item for testing the content table view."""

    id: str
    name: str
    value: int
    category: str


class ItemSampleTableModel(BaseTableModel[ItemSample]):
    """Table model for testing the content table view."""

    COLUMNS = (
        Column[ItemSample](
            header="ID",
            tooltip="Test item ID",
            getter=lambda item: item.id,
        ),
        Column[ItemSample](
            header="Name",
            tooltip="Test item name",
            getter=lambda item: item.name,
        ),
        Column[ItemSample](
            header="Value",
            tooltip="Test item value",
            getter=lambda item: item.value,
        ),
        Column[ItemSample](
            header="Category",
            tooltip="Test item category",
            getter=lambda item: item.category,
            sortable=False,
            filterable=False,
        ),
    )


def create_items() -> list[ItemSample]:
    """Create test items.

    :returns: Test items.
    """
    return [
        ItemSample(id="y", name="Apple", value=30, category="A3"),
        ItemSample(id="x", name="Orange", value=10, category="A1"),
        ItemSample(id="z", name="Banana", value=20, category="A2"),
    ]
