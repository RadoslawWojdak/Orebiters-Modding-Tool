from collections.abc import Callable, Sequence

from PySide6.QtWidgets import QComboBox, QWidget


class DynamicComboBox[T](QComboBox):
    """Combo box with dynamically refreshed choices."""

    def __init__(
        self,
        choices_provider: Callable[[T | None], Sequence[T]],
        choice_formatter: Callable[[T], str] = str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._choices_provider = choices_provider
        self._choice_formatter = choice_formatter

        self._refresh_choices()

    def showPopup(self) -> None:
        """Refresh choices before showing the popup."""
        self._refresh_choices()
        super().showPopup()

    def find_data_equal(self, value: T) -> int:
        """Find the index of data equal to the given value.

        Unlike QComboBox.findData(), this method compares values using Python
        equality, which allows it to find equivalent but distinct objects.
        """
        return next((index for index in range(self.count()) if self.itemData(index) == value), -1)

    def _refresh_choices(self) -> None:
        """Refresh choices from the provider."""
        current_value = self.currentData()
        choices = self._choices_provider(current_value)

        self.blockSignals(True)
        try:
            self.clear()

            for choice in choices:
                self.addItem(self._choice_formatter(choice), choice)

            if current_value is not None:
                index = self.find_data_equal(current_value)

                if index >= 0:
                    self.setCurrentIndex(index)
                else:
                    self.setCurrentIndex(-1)
            else:
                self.setCurrentIndex(-1)
        finally:
            self.blockSignals(False)
