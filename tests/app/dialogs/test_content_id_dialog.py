from PySide6.QtWidgets import QApplication, QDialog, QLineEdit

from orebiters_modding_tool.app.dialogs.content_id_dialog import ContentIdDialog
from orebiters_modding_tool.domain.content import ContentType


def test_initializes_dialog(qapp: QApplication) -> None:
    """Initialize the dialog with its expected UI structure."""
    dialog = ContentIdDialog(ContentType.MATERIALS, lambda _: None)

    assert dialog.windowTitle() == "Create Material"
    assert dialog.isModal()
    assert isinstance(dialog._id_edit, QLineEdit)
    assert dialog._id_edit.placeholderText() == "Unique content ID"
    assert dialog._error_label.isHidden()
    assert dialog._button_box.standardButtons() == (
        dialog._button_box.StandardButton.Ok | dialog._button_box.StandardButton.Cancel
    )


def test_try_accept_calls_on_create_for_valid_id(qapp: QApplication) -> None:
    """Call the creation callback for a valid ID."""
    created_ids: list[str] = []
    dialog = ContentIdDialog(ContentType.MATERIALS, created_ids.append)
    dialog._id_edit.setText("my_material")

    dialog._try_accept()

    assert created_ids == ["my_material"]
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_try_accept_normalizes_id_before_creation(qapp: QApplication) -> None:
    """Normalize the ID before calling the creation callback."""
    created_ids: list[str] = []
    dialog = ContentIdDialog(ContentType.MATERIALS, created_ids.append)
    dialog._id_edit.setText(" My Material ")

    dialog._try_accept()

    assert created_ids == ["my_material"]
    assert dialog._id_edit.text() == "my_material"


def test_try_accept_shows_error_for_empty_id(qapp: QApplication) -> None:
    """Show an error when the entered ID is empty."""
    created_ids: list[str] = []
    dialog = ContentIdDialog(ContentType.MATERIALS, created_ids.append)

    dialog._try_accept()

    assert created_ids == []
    assert dialog._error_label.text() == "ID cannot be empty."
    assert not dialog._error_label.isHidden()


def test_try_accept_shows_error_for_already_existing_id(qapp: QApplication) -> None:
    """Show an error when the entered ID already exists."""

    def on_create(_: str) -> None:
        raise ValueError("Material already exists.")

    dialog = ContentIdDialog(ContentType.MATERIALS, on_create)
    dialog._id_edit.setText("existing_material")

    dialog._try_accept()

    assert dialog.result() == QDialog.DialogCode.Rejected
    assert dialog._error_label.text() == "Material already exists."
    assert not dialog._error_label.isHidden()


def test_show_error_displays_message_and_selects_id(qapp: QApplication) -> None:
    """Display the error message and select the entered ID."""
    dialog = ContentIdDialog(ContentType.MATERIALS, lambda _: None)
    dialog._id_edit.setText("invalid")

    dialog._show_error("Invalid ID.")

    assert dialog._error_label.text() == "Invalid ID."
    assert not dialog._error_label.isHidden()
    assert dialog._id_edit.selectedText() == "invalid"


def test_cancel_button_rejects_dialog(qapp: QApplication) -> None:
    """Reject the dialog when the cancel button is clicked."""
    dialog = ContentIdDialog(ContentType.MATERIALS, lambda _: None)

    dialog._button_box.rejected.emit()

    assert dialog.result() == QDialog.DialogCode.Rejected
