from orebiters_modding_tool.app.models.material_table_model import MaterialTableModel
from orebiters_modding_tool.domain.content import ContentType
from tests.factories.material_factory import MaterialFactory
from tests.factories.material_requirement_factory import MaterialRequirementFactory


def _get_column(header: str):
    """Return column using header."""
    return next(column for column in MaterialTableModel.COLUMNS if column.header == header)


def test_content_type() -> None:
    """Use the materials content type."""
    assert MaterialTableModel.CONTENT_TYPE == ContentType.MATERIALS


def test_row_count_returns_number_of_materials() -> None:
    """Test that row count matches the number of materials."""
    materials = [MaterialFactory.create() for _ in range(3)]

    model = MaterialTableModel(materials)

    assert model.rowCount() == 3


def test_name_column_returns_english_localization() -> None:
    """Test that name column returns the English localization."""
    item = MaterialFactory.create()
    item.localizations["en"].one = "Clay"

    name_column = _get_column("Name")

    assert name_column.getter(item) == "Clay"


def test_craftable_column_returns_checkmark_for_craftable_material() -> None:
    """Test that craftable column identifies materials with crafting materials."""
    material = MaterialFactory.create(crafting_materials=[MaterialRequirementFactory.create()])

    craftable_column = _get_column("Craftable")

    assert craftable_column.getter(material) == "✔️"


def test_craftable_column_returns_empty_string_for_non_craftable_material() -> None:
    """Test that craftable column is empty when the material has no crafting materials."""
    material = MaterialFactory.create(crafting_materials=[])

    craftable_column = _get_column("Craftable")

    assert craftable_column.getter(material) == ""
