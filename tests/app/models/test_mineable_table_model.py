import pytest

from orebiters_modding_tool.app.models.mineable_table_model import MineableTableModel
from orebiters_modding_tool.domain.content import ContentType
from tests.factories.mineable_factory import MineableFactory


def _get_column(header: str):
    """Return column using header."""
    return next(column for column in MineableTableModel.COLUMNS if column.header == header)


def test_content_type() -> None:
    """Use the mineables content type."""
    assert MineableTableModel.CONTENT_TYPE == ContentType.MINEABLES


def test_row_count_returns_number_of_mineables() -> None:
    """Test that row count matches the number of mineables."""
    mineables = [MineableFactory.create() for _ in range(3)]

    model = MineableTableModel(mineables)

    assert model.rowCount() == 3


def test_name_column_uses_english_localization() -> None:
    """Display the English localization as the mineable name."""
    mineable = MineableFactory.create()
    mineable.localizations["en"].one = "Iron"

    name_column = _get_column("Name")

    assert name_column.getter(mineable) == "Iron"


@pytest.mark.parametrize(
    ("min_depth", "max_depth", "expected"),
    [
        (10, 50, "10 – 50"),
        (None, 50, "0 – 50"),
        (10, None, "10 – ∞"),
        (None, None, "0 – ∞"),
    ],
)
def test_depth_column_formats_depth_range(
    min_depth: int | None,
    max_depth: int | None,
    expected: str,
) -> None:
    """Format the mineable depth range for display."""
    mineable = MineableFactory.create(min_depth=min_depth, max_depth=max_depth)

    depth_column = _get_column("Depth")

    assert depth_column.getter(mineable) == expected


@pytest.mark.parametrize(
    ("min_depth", "max_depth", "expected"),
    [
        (10, 50, (10, 50)),
        (None, 50, (0, 50)),
        (10, None, (10, float("inf"))),
        (None, None, (0, float("inf"))),
    ],
)
def test_depth_column_sorts_by_numeric_depth_range(
    min_depth: int | None,
    max_depth: int | None,
    expected: tuple[int, int | float],
) -> None:
    """Return numeric depth bounds suitable for sorting."""
    mineable = MineableFactory.create(min_depth=min_depth, max_depth=max_depth)

    depth_column = _get_column("Depth")

    assert depth_column.sorter is not None
    assert depth_column.sorter(mineable) == expected
