from PySide6.QtWidgets import QApplication

from orebiters_modding_tool.app.models.column import Column
from orebiters_modding_tool.app.models.content_table_model import ContentTableModel
from orebiters_modding_tool.domain.content import Content, ContentState
from tests.factories.content import ContentFactory


class ContentTableModelSample(ContentTableModel[Content]):
    """Table model used for testing the content table model."""

    COLUMNS = (
        Column(
            header="Name",
            getter=lambda item: item.id,
            setter=lambda item, value: setattr(item, "id", value),
            tooltip="Content ID",
        ),
    )


def create_model() -> ContentTableModelSample:
    """Create a test table model."""
    return ContentTableModelSample(
        [
            ContentFactory.create(state=ContentState.SAVED),
            ContentFactory.create(state=ContentState.MODIFIED),
        ]
    )


def test_data_returns_content_state(qapp: QApplication) -> None:
    """Return the content state for the content state role."""
    model = create_model()
    index = model.index(0, 0)

    assert model.data(index, ContentTableModel.CONTENT_STATE_ROLE) is model.get_item(0).state


def test_refresh_content_states_emits_state_change(qapp: QApplication) -> None:
    """Emit a data change for all content states."""
    model = create_model()

    changes: list[tuple] = []
    model.dataChanged.connect(
        lambda top_left, bottom_right, roles: changes.append((top_left, bottom_right, roles))
    )

    model.refresh_content_states()

    assert len(changes) == 1

    top_left, bottom_right, roles = changes[0]

    assert top_left == model.index(0, 0)
    assert bottom_right == model.index(model.rowCount() - 1, model.columnCount() - 1)
    assert roles == [ContentTableModel.CONTENT_STATE_ROLE]


def test_refresh_content_states_does_nothing_for_empty_model(qapp: QApplication) -> None:
    """Do nothing when the content model is empty."""
    model = ContentTableModelSample([])

    changes: list[tuple] = []
    model.dataChanged.connect(
        lambda top_left, bottom_right, roles: changes.append((top_left, bottom_right, roles))
    )

    model.refresh_content_states()

    assert changes == []
