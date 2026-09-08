from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class WelcomeWidget(QWidget):
    """Welcome screen displayed in the workspace."""

    TITLE_TEXT = "Orebiters Modding Tool"
    MESSAGE_TEXT = "Select content from the Project Explorer or create new content to get started."
    STEAM_LINK_TEXT = "Orebiters on Steam"

    STEAM_URL = (
        "https://store.steampowered.com/app/4253410/Orebiters/"
        "?utm_source=orebiters_modding_tool"
        "&utm_medium=in_app"
        "&utm_campaign=welcome_screen"
    )

    TITLE_FONT_SIZE = 24
    MESSAGE_FONT_SIZE = 12
    LINK_FONT_SIZE = 11
    CONTENT_SPACING = 24
    LINK_SPACING = 12

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the welcome screen."""
        super().__init__(parent)

        self._setup_layout()

    def _setup_layout(self) -> None:
        """Set up the welcome screen layout."""
        layout = QVBoxLayout(self)

        layout.addStretch()
        layout.addWidget(self._create_title_label())
        layout.addSpacing(self.CONTENT_SPACING)
        layout.addWidget(self._create_message_label())
        layout.addSpacing(self.LINK_SPACING)
        layout.addWidget(self._create_steam_link())
        layout.addStretch()

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

    def _create_steam_link(self) -> QLabel:
        """Create the Steam link label.

        :returns: Configured Steam link label.
        """
        link_label = QLabel(self.STEAM_LINK_TEXT, self)
        link_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        link_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        link_label.setCursor(Qt.CursorShape.PointingHandCursor)
        link_label.setOpenExternalLinks(True)
        link_label.setText(f'<a href="{self.STEAM_URL}">{self.STEAM_LINK_TEXT}</a>')

        font = QFont(link_label.font())
        font.setPointSize(self.LINK_FONT_SIZE)

        link_label.setFont(font)

        return link_label
