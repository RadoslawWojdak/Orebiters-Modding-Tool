from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QRadioButton, QStackedWidget, QVBoxLayout, QWidget


class _VariantStackedWidget(QStackedWidget):
    """Stacked widget sized according to its current page."""

    def sizeHint(self) -> QSize:
        """Return the size hint of the current page."""
        page = self.currentWidget()
        if page is None:
            return QSize(0, 0)

        return page.sizeHint()

    def minimumSizeHint(self) -> QSize:
        """Return the minimum size hint of the current page."""
        page = self.currentWidget()
        if page is None:
            return QSize(0, 0)

        return page.minimumSizeHint()


class VariantWidget[T](QWidget):
    """Widget for selecting and displaying a variant."""

    variant_changed = Signal(int)

    def __init__(
        self,
        variants: list[tuple[str, QWidget, T]],
        initial_index: int | None = None,
        parent: QWidget | None = None,
        *,
        read_only: bool = False,
    ) -> None:
        """Initialize the variant widget.

        :param variants: Available variants with labels, pages, and payloads.
        :param initial_index: Index of the initially selected variant.
        :param parent: Optional parent widget.
        :param read_only: Whether variant selection is disabled.
        """
        super().__init__(parent)

        if not variants:
            raise ValueError("VariantWidget requires at least one variant.")

        self._payloads = [payload for _, _, payload in variants]

        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)

        self._stacked_widget = _VariantStackedWidget(self)
        self._stacked_widget.setMinimumSize(0, 0)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)

        for index, (label, page, _) in enumerate(variants):
            button = QRadioButton(label, self)
            button.setEnabled(not read_only)

            self._button_group.addButton(button, index)
            self._layout.addWidget(button)
            self._stacked_widget.addWidget(page)

        self._layout.addWidget(self._stacked_widget, 0, Qt.AlignmentFlag.AlignTop)

        self._button_group.idClicked.connect(self._on_variant_clicked)

        self._active_index: int | None = None
        self._set_active_variant(None)

        if initial_index is not None:
            self.set_active_variant(initial_index)

    @property
    def active_index(self) -> int | None:
        """Return the index of the active variant."""
        return self._active_index

    @property
    def payloads(self) -> tuple[T, ...]:
        """Return the payloads of all variants."""
        return tuple(self._payloads)

    @property
    def active_payload(self) -> T | None:
        """Return the payload of the active variant."""
        index = self.active_index
        return self._payloads[index] if index is not None else None

    def set_active_variant(self, index: int) -> None:
        """Set the active variant.

        :param index: Index of the variant to activate.
        """
        self._validate_index(index)

        if not 0 <= index < len(self._payloads):
            raise IndexError(f"Variant index out of range: {index}")

        self._set_active_variant(index)

    def _on_variant_clicked(self, index: int) -> None:
        """Handle variant selection.

        :param index: Index of the selected variant.
        """
        self._set_active_variant(index)
        self.variant_changed.emit(index)

    def _set_active_variant(self, index: int | None) -> None:
        """Update the active variant and its visibility.

        :param index: Index of the variant to activate, or None to clear selection.
        """
        self._active_index = index

        if index is None:
            self._button_group.setExclusive(False)
            for button in self._button_group.buttons():
                button.setChecked(False)
            self._button_group.setExclusive(True)

            self._stacked_widget.hide()
        else:
            self._button_group.button(index).setChecked(True)
            self._stacked_widget.setCurrentIndex(index)
            self._stacked_widget.show()

        self._stacked_widget.updateGeometry()
        self.updateGeometry()

    @staticmethod
    def _validate_index(index: int) -> None:
        """Validate the variant index.

        :param index: Index to validate.
        """
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError("Variant index must be an integer.")
