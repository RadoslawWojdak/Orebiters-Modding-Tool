from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QLineEdit

from orebiters_modding_tool.app.dialogs.new_project_dialog import NewProjectDialog


def test_initializes_dialog(qapp: QApplication) -> None:
    """Initialize the dialog with its expected UI structure."""
    dialog = NewProjectDialog()

    assert dialog.windowTitle() == "New Project"
    assert isinstance(dialog._namespace_input, QLineEdit)
    assert isinstance(dialog._name_input, QLineEdit)
    assert dialog._qualified_id_label.text() == "-"
    assert dialog._namespace_input.validator() is not None
    assert dialog._name_input.validator() is not None


def test_namespace_returns_entered_namespace(qapp: QApplication) -> None:
    """Return the entered project namespace."""
    dialog = NewProjectDialog()
    dialog._namespace_input.setText("orebiters")

    assert dialog.namespace == "orebiters"


def test_name_returns_entered_name(qapp: QApplication) -> None:
    """Return the entered project name."""
    dialog = NewProjectDialog()
    dialog._name_input.setText("core")

    assert dialog.name == "core"


def test_update_qualified_id_shows_placeholder_when_inputs_are_empty(qapp: QApplication) -> None:
    """Show a placeholder when both project inputs are empty."""
    dialog = NewProjectDialog()

    dialog._update_qualified_id()

    assert dialog._qualified_id_label.text() == "-"


def test_update_qualified_id_shows_qualified_id_for_entered_values(qapp: QApplication) -> None:
    """Show the qualified ID for the entered namespace and project name."""
    dialog = NewProjectDialog()
    dialog._namespace_input.setText("orebiters")
    dialog._name_input.setText("Core")

    assert dialog._qualified_id_label.text() == "orebiters.core"


def test_update_qualified_id_normalizes_entered_values(qapp: QApplication) -> None:
    """Normalize the namespace and project name before creating the qualified ID."""
    dialog = NewProjectDialog()
    dialog._namespace_input.setText(" Orebiters ")
    dialog._name_input.setText("My Project")

    assert dialog._qualified_id_label.text() == "orebiters.my_project"


def test_update_qualified_id_updates_when_namespace_changes(qapp: QApplication) -> None:
    """Update the qualified ID when the namespace changes."""
    dialog = NewProjectDialog()
    dialog._namespace_input.setText("orebiters")
    dialog._name_input.setText("core")

    assert dialog._qualified_id_label.text() == "orebiters.core"

    dialog._namespace_input.setText("example")

    assert dialog._qualified_id_label.text() == "example.core"


def test_update_qualified_id_updates_when_name_changes(qapp: QApplication) -> None:
    """Update the qualified ID when the project name changes."""
    dialog = NewProjectDialog()
    dialog._namespace_input.setText("orebiters")
    dialog._name_input.setText("core")

    assert dialog._qualified_id_label.text() == "orebiters.core"

    dialog._name_input.setText("tools")

    assert dialog._qualified_id_label.text() == "orebiters.tools"


def test_accept_button_accepts_dialog(qapp: QApplication) -> None:
    """Accept the dialog when the OK button is clicked."""
    dialog = NewProjectDialog()
    button_box = dialog.findChild(QDialogButtonBox)

    assert button_box is not None

    button_box.accepted.emit()

    assert dialog.result() == QDialog.DialogCode.Accepted


def test_cancel_button_rejects_dialog(qapp: QApplication) -> None:
    """Reject the dialog when the cancel button is clicked."""
    dialog = NewProjectDialog()
    button_box = dialog.findChild(QDialogButtonBox)

    assert button_box is not None

    button_box.rejected.emit()

    assert dialog.result() == QDialog.DialogCode.Rejected
