from collections.abc import Callable

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from orebiters_modding_tool.domain.content import ContentType
from orebiters_modding_tool.domain.project_identifier import normalize_identifier


class ContentIdDialog(QDialog):
    """Dialog for creating content."""

    def __init__(
        self,
        content_type: ContentType,
        on_create: Callable[[str], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._content_type = content_type

        self.setWindowTitle(f"Create {content_type.singular_display_name}")
        self.setModal(True)

        self._on_create = on_create

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        self._id_edit = QLineEdit(self)
        self._id_edit.setPlaceholderText("Unique content ID")

        self._error_label = QLabel(self)
        self._error_label.setStyleSheet("color: red;")
        self._error_label.setWordWrap(True)
        self._error_label.hide()

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )

        content_name = self._content_type.singular_display_name.lower()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Enter a unique ID for the new {content_name}:", self))
        layout.addWidget(self._id_edit)
        layout.addWidget(self._error_label)
        layout.addWidget(self._button_box)

    def _setup_connections(self) -> None:
        """Set up dialog signal connections."""
        self._button_box.accepted.connect(self._try_accept)
        self._button_box.rejected.connect(self.reject)

    def _try_accept(self) -> None:
        """Try to create content with the entered ID."""
        content_id = normalize_identifier(self._id_edit.text())

        if not content_id:
            self._show_error("ID cannot be empty.")
            return

        self._id_edit.setText(content_id)
        self._error_label.hide()

        try:
            self._on_create(content_id)
        except ValueError as error:
            self._show_error(str(error))
            return

        self.accept()

    def _show_error(self, message: str) -> None:
        """Show a validation error.

        :param message: Error message.
        """
        self._error_label.setText(message)
        self._error_label.show()
        self._id_edit.setFocus()
        self._id_edit.selectAll()
