from PySide6.QtGui import QColor, QPainter, QPalette
from PySide6.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem

from orebiters_modding_tool.app.models.base_table_model import ModelIndex
from orebiters_modding_tool.app.models.content_table_model import ContentTableModel
from orebiters_modding_tool.domain.content import ContentState


class ContentTableDelegate(QStyledItemDelegate):
    """Delegate responsible for styling content table items."""

    SELECTION_ALPHA = 80
    STATE_ACCENT_BLEND_RATIO = 0.12

    NEW_ACCENT = QColor("#E6B800")
    MODIFIED_ACCENT = QColor("#357ABD")

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: ModelIndex) -> None:
        """Paint a content table item.

        :param painter: Painter used for rendering.
        :param option: Style options for the item.
        :param index: Model index being painted.
        """
        option = self._prepare_option(option)

        state = index.data(ContentTableModel.CONTENT_STATE_ROLE)
        if not isinstance(state, ContentState):
            state = None

        self._paint_background(painter, option, index, state)
        self._paint_selection(painter, option)

        option.state &= ~QStyle.StateFlag.State_Selected

        super().paint(painter, option, index)

    @staticmethod
    def _prepare_option(option: QStyleOptionViewItem) -> QStyleOptionViewItem:
        """Prepare style options for custom rendering.

        :param option: Original style options.
        :returns: Copy of the style options adjusted for custom rendering.
        """
        option = QStyleOptionViewItem(option)
        option.state &= ~QStyle.StateFlag.State_MouseOver
        option.state &= ~QStyle.StateFlag.State_HasFocus

        return option

    @classmethod
    def _paint_background(
        cls,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: ModelIndex,
        state: ContentState | None,
    ) -> None:
        """Paint the item's background.

        :param painter: Painter used for rendering.
        :param option: Style options containing the palette.
        :param index: Model index being painted.
        :param state: Content persistence state.
        """
        background = cls._get_background(index, state, option.palette)

        painter.fillRect(option.rect, background)

    @classmethod
    def _paint_selection(cls, painter: QPainter, option: QStyleOptionViewItem) -> None:
        """Paint the item's selection overlay.

        :param painter: Painter used for rendering.
        :param option: Style options containing selection state.
        """
        if not option.state & QStyle.StateFlag.State_Selected:
            return

        selection_color = option.palette.color(QPalette.ColorRole.Highlight)
        selection_color.setAlpha(cls.SELECTION_ALPHA)

        painter.fillRect(option.rect, selection_color)

    @classmethod
    def _get_background(
        cls,
        index: ModelIndex,
        state: ContentState | None,
        palette: QPalette,
    ) -> QColor:
        """Return the background color for an item.

        :param index: Model index being painted.
        :param state: Content persistence state.
        :param palette: Palette used by the current Qt style.
        :returns: Background color for the item.
        """
        base = cls._get_base_background(index, palette)

        match state:
            case ContentState.NEW:
                return cls._blend_with_base(base, cls.NEW_ACCENT)

            case ContentState.MODIFIED:
                return cls._blend_with_base(base, cls.MODIFIED_ACCENT)

            case _:
                return base

    @staticmethod
    def _get_base_background(index: ModelIndex, palette: QPalette) -> QColor:
        """Return the default background for a table row.

        :param index: Model index being painted.
        :param palette: Palette used by the current Qt style.
        :returns: Base or alternate base color.
        """
        role = QPalette.ColorRole.AlternateBase if index.row() % 2 else QPalette.ColorRole.Base

        return palette.color(role)

    @classmethod
    def _blend_with_base(cls, base: QColor, accent: QColor) -> QColor:
        """Blend an accent color with a base color.

        :param base: Base background color.
        :param accent: Accent color.
        :returns: Blended background color.
        """
        blend_ratio = cls.STATE_ACCENT_BLEND_RATIO

        return QColor(
            round(base.red() * (1 - blend_ratio) + accent.red() * blend_ratio),
            round(base.green() * (1 - blend_ratio) + accent.green() * blend_ratio),
            round(base.blue() * (1 - blend_ratio) + accent.blue() * blend_ratio),
        )
