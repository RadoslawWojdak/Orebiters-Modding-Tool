from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QPalette, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from orebiters_modding_tool.domain.project_identifier import (
    create_qualified_id,
    normalize_identifier,
)


class NewProjectDialog(QDialog):
    """Dialog used to collect information for a new project."""

    _IDENTIFIER_PATTERN = QRegularExpression("[a-zA-Z0-9_ ]*")

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the new project dialog.

        :param parent: Optional parent widget.
        """
        super().__init__(parent)

        self.setWindowTitle("New Project")

        self._setup_layout()
        self._update_qualified_id()

    @property
    def namespace(self) -> str:
        """Return the entered project namespace."""
        return self._namespace_input.text()

    @property
    def name(self) -> str:
        """Return the entered project name."""
        return self._name_input.text()

    def _setup_layout(self) -> None:
        """Set up the new project dialog layout."""
        self._namespace_input = QLineEdit(self)
        self._name_input = QLineEdit(self)
        self._qualified_id_label = self._create_qualified_id_label()

        self._namespace_input.setValidator(
            QRegularExpressionValidator(self._IDENTIFIER_PATTERN, self),
        )
        self._name_input.setValidator(
            QRegularExpressionValidator(self._IDENTIFIER_PATTERN, self),
        )

        form_layout = QFormLayout()
        form_layout.addRow("Namespace:", self._namespace_input)
        form_layout.addRow("Project name:", self._name_input)
        form_layout.addRow(self._qualified_id_label)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addLayout(self._create_button_layout())

        self._namespace_input.textChanged.connect(self._update_qualified_id)
        self._name_input.textChanged.connect(self._update_qualified_id)

    def _create_qualified_id_label(self) -> QLabel:
        """Create the qualified ID preview label.

        :returns: Configured qualified ID label.
        """
        label = QLabel(self)

        palette = label.palette()
        palette.setColor(label.foregroundRole(), palette.color(QPalette.ColorRole.Mid))

        label.setPalette(palette)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        return label

    def _create_button_layout(self) -> QHBoxLayout:
        """Create the dialog button layout.

        :returns: Configured button layout.
        """
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(button_box)
        button_layout.addStretch()

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        return button_layout

    def _update_qualified_id(self) -> None:
        """Update the qualified ID preview."""
        namespace = normalize_identifier(self._namespace_input.text())
        mod_id = normalize_identifier(self._name_input.text())

        if not namespace and not mod_id:
            self._qualified_id_label.setText("-")
            return

        qualified_id = create_qualified_id(namespace, mod_id)

        self._qualified_id_label.setText(f"{qualified_id}")
