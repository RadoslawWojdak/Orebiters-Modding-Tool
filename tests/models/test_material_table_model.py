from orebiters_modding_tool.domain.material import MaterialRequirement
from orebiters_modding_tool.models.material_table_model import MaterialTableModel
from tests.factories.content import ContentReferenceFactory
from tests.factories.material import MaterialFactory


def test_row_count_returns_number_of_materials() -> None:
    """Test that row count matches the number of materials."""

    materials = [MaterialFactory.create() for _ in range(3)]

    model = MaterialTableModel(materials)

    assert model.rowCount() == 3


def test_craftable_column_returns_true_for_craftable_material() -> None:
    """Test that craftable column identifies craftable materials."""

    clay = MaterialFactory.create(id="clay")

    mud_patch_mix = MaterialFactory.create(
        id="mud_patch_mix",
        crafting_materials=[
            MaterialRequirement(
                material=ContentReferenceFactory.from_content(clay, mod_id="core"),
                amount=1,
            ),
        ],
    )

    model = MaterialTableModel([mud_patch_mix])

    craftable_index = model.index(0, 3)

    assert model.data(craftable_index) == "✔️"
