from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class WelcomeWidget(QWidget):
    """Welcome screen displayed in the workspace."""

    TITLE_TEXT = "Orebiters Modding Tool"
    MESSAGE_TEXT = "Select content from the Project Explorer or create new content to get started."

    TITLE_FONT_SIZE = 24
    MESSAGE_FONT_SIZE = 12
    CONTENT_SPACING = 24

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._setup_layout()

    def _setup_layout(self) -> None:
        """Set up the welcome screen layout."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = self._create_title_label()
        message_label = self._create_message_label()

        layout.addWidget(title_label)
        layout.addSpacing(self.CONTENT_SPACING)
        layout.addWidget(message_label)

    def _create_title_label(self) -> QLabel:
        """Create the welcome screen title label.

        :returns: Configured title label.
        """
        title_label = QLabel(self.TITLE_TEXT, self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = QFont(title_label.font())
        font.setPointSize(self.TITLE_FONT_SIZE)
        font.setBold(True)

        title_label.setFont(font)

        return title_label

    def _create_message_label(self) -> QLabel:
        """Create the welcome screen message label.

        :returns: Configured message label.
        """
        message_label = QLabel(self.MESSAGE_TEXT, self)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)

        font = QFont(message_label.font())
        font.setPointSize(self.MESSAGE_FONT_SIZE)

        message_label.setFont(font)

        return message_label
