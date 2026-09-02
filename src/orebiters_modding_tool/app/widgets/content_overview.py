from dataclasses import dataclass

from PySide6.QtCore import QAbstractItemModel, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QStackedLayout, QVBoxLayout, QWidget

from orebiters_modding_tool.app.widgets.content_table_view import ContentTableView
from orebiters_modding_tool.domain.content import ContentReference


@dataclass(frozen=True, slots=True, kw_only=True)
class ContentOverviewConfig:
    """Configuration for a content overview widget."""

    title: str
    empty_message: str


class ContentOverviewWidget(QWidget):
    """Content overview displayed in the workspace."""

    TITLE_FONT_SIZE = 24
    TITLE_CONTENT_SPACING = 24
    MESSAGE_FONT_SIZE = 12

    def __init__(
        self,
        content_reference: ContentReference,
        config: ContentOverviewConfig,
        model: QAbstractItemModel,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._content_reference = content_reference
        self._model = model
        self._config = config

        self._setup_layout()
        self._connect_signals()
        self._update_content_visibility()

    @property
    def content_reference(self) -> ContentReference:
        """Return the reference represented by this widget.

        :returns: Content reference.
        """
        return self._content_reference

    def _setup_layout(self) -> None:
        """Set up the content overview layout."""
        layout = QVBoxLayout(self)

        layout.addStretch()
        layout.addWidget(self._create_title_label())
        layout.addSpacing(self.TITLE_CONTENT_SPACING)
        layout.addLayout(self._create_content_layout())
        layout.addStretch()

    def _create_content_layout(self) -> QStackedLayout:
        """Create the content overview layout.

        :returns: Configured content layout.
        """
        self._content_layout = QStackedLayout()

        self._message_label = self._create_message_label()
        self._table_view = ContentTableView(self._model, self)

        self._content_layout.addWidget(self._message_label)
        self._content_layout.addWidget(self._table_view)

        return self._content_layout

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self._model.rowsInserted.connect(self._update_content_visibility)
        self._model.rowsRemoved.connect(self._update_content_visibility)
        self._model.modelReset.connect(self._update_content_visibility)

    def _update_content_visibility(self) -> None:
        """Update the visible content state."""
        if self._model.rowCount() == 0:
            self._content_layout.setCurrentWidget(self._message_label)
        else:
            self._content_layout.setCurrentWidget(self._table_view)

    def _create_title_label(self) -> QLabel:
        """Create the content overview title label.

        :returns: Configured title label.
        """
        title_label = QLabel(self._config.title, self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = QFont(title_label.font())
        font.setPointSize(self.TITLE_FONT_SIZE)
        font.setBold(True)

        title_label.setFont(font)

        return title_label

    def _create_message_label(self) -> QLabel:
        """Create the content overview message label.

        :returns: Configured message label.
        """
        message_label = QLabel(self._config.empty_message, self)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)

        font = QFont(message_label.font())
        font.setPointSize(self.MESSAGE_FONT_SIZE)

        message_label.setFont(font)

        return message_label
