from orebiters_modding_tool.app.models.item_table_model import ItemTableModel
from orebiters_modding_tool.domain.content import ContentType
from tests.factories.item_factory import ItemFactory
from tests.factories.material_requirement_factory import MaterialRequirementFactory


def _get_column(header: str):
    """Return column using header."""
    return next(column for column in ItemTableModel.COLUMNS if column.header == header)


def test_content_type() -> None:
    """Use the items content type."""
    assert ItemTableModel.CONTENT_TYPE == ContentType.ITEMS


def test_row_count_returns_number_of_items() -> None:
    """Test that row count matches the number of items."""
    items = [ItemFactory.create() for _ in range(3)]

    model = ItemTableModel(items)

    assert model.rowCount() == 3


def test_name_column_returns_english_localization() -> None:
    """Test that name column returns the English localization."""
    item = ItemFactory.create()
    item.localizations["en"].one = "Fuel Canister"

    name_column = _get_column("Name")

    assert name_column.getter(item) == "Fuel Canister"


def test_craftable_column_returns_checkmark_for_craftable_item() -> None:
    """Test that craftable column identifies items with crafting materials."""
    item = ItemFactory.create(crafting_materials=[MaterialRequirementFactory.create()])

    craftable_column = _get_column("Craftable")

    assert craftable_column.getter(item) == "✔️"


def test_craftable_column_returns_empty_string_for_non_craftable_item() -> None:
    """Test that craftable column is empty when the item has no crafting materials."""
    item = ItemFactory.create(crafting_materials=[])

    craftable_column = _get_column("Craftable")

    assert craftable_column.getter(item) == ""
