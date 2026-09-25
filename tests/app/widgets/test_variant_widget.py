import pytest
from PySide6.QtCore import QSize
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication, QLabel, QRadioButton, QWidget

from orebiters_modding_tool.app.widgets.variant_widget import VariantWidget, _VariantStackedWidget


class SizedWidget(QWidget):
    """Widget with configurable size hints for testing."""

    def __init__(self, size: QSize) -> None:
        super().__init__()
        self._size = size

    def sizeHint(self) -> QSize:
        return self._size

    def minimumSizeHint(self) -> QSize:
        return self._size


def _create_variants() -> list[tuple[str, QWidget, object]]:
    """Create variants for testing."""
    return [
        ("First", QLabel("First page"), "first payload"),
        ("Second", QLabel("Second page"), "second payload"),
        ("Third", QLabel("Third page"), "third payload"),
    ]


def test_creates_variant_selection_for_each_variant(qapp: QApplication) -> None:
    """Create a selectable option for every variant."""
    widget = VariantWidget(_create_variants())

    buttons = widget.findChildren(QRadioButton)

    assert [button.text() for button in buttons] == ["First", "Second", "Third"]


def test_starts_without_active_variant(qapp: QApplication) -> None:
    """Start without an active variant when no initial index is provided."""
    widget = VariantWidget(_create_variants())

    assert widget.active_index is None
    assert widget.active_payload is None


def test_initial_index_selects_variant(qapp: QApplication) -> None:
    """Select the configured initial variant."""
    widget = VariantWidget(_create_variants(), initial_index=1)

    assert widget.active_index == 1
    assert widget.active_payload == "second payload"


def test_initial_index_displays_selected_page(qapp: QApplication) -> None:
    """Display the page belonging to the initially selected variant."""
    variants = _create_variants()

    widget = VariantWidget(variants, initial_index=1)

    assert widget._stacked_widget.currentWidget() is variants[1][1]


def test_set_active_variant_changes_selection(qapp: QApplication) -> None:
    """Change the active variant programmatically."""
    widget = VariantWidget(_create_variants(), initial_index=0)

    widget.set_active_variant(2)

    assert widget.active_index == 2
    assert widget.active_payload == "third payload"


def test_set_active_variant_displays_selected_page(qapp: QApplication) -> None:
    """Display the page belonging to the selected variant."""
    variants = _create_variants()
    widget = VariantWidget(variants, initial_index=0)

    widget.set_active_variant(2)

    assert widget._stacked_widget.currentWidget() is variants[2][1]


def test_clicking_variant_changes_selection(qapp: QApplication) -> None:
    """Change the active variant when the user clicks an option."""
    widget = VariantWidget(_create_variants())

    widget.findChildren(QRadioButton)[1].click()

    assert widget.active_index == 1
    assert widget.active_payload == "second payload"


def test_clicking_variant_displays_selected_page(qapp: QApplication) -> None:
    """Display the page belonging to the clicked variant."""
    variants = _create_variants()
    widget = VariantWidget(variants)

    widget.findChildren(QRadioButton)[2].click()

    assert widget._stacked_widget.currentWidget() is variants[2][1]


def test_clicking_variant_emits_variant_changed(qapp: QApplication) -> None:
    """Emit the selected index when the user changes the variant."""
    widget = VariantWidget(_create_variants())
    spy = QSignalSpy(widget.variant_changed)

    widget.findChildren(QRadioButton)[1].click()

    assert spy.count() == 1
    assert spy.at(0)[0] == 1


def test_programmatic_selection_does_not_emit_variant_changed(qapp: QApplication) -> None:
    """Do not emit variant_changed for programmatic selection."""
    widget = VariantWidget(_create_variants())
    spy = QSignalSpy(widget.variant_changed)

    widget.set_active_variant(1)

    assert spy.count() == 0


def test_only_active_variant_is_selected(qapp: QApplication) -> None:
    """Keep only the active variant selected."""
    widget = VariantWidget(_create_variants(), initial_index=0)

    buttons = widget.findChildren(QRadioButton)

    widget.set_active_variant(2)

    assert [button.isChecked() for button in buttons] == [False, False, True]


def test_read_only_disables_variant_selection(qapp: QApplication) -> None:
    """Disable user selection in read-only mode."""
    widget = VariantWidget(_create_variants(), initial_index=1, read_only=True)

    buttons = widget.findChildren(QRadioButton)

    assert all(not button.isEnabled() for button in buttons)
    assert widget.active_index == 1
    assert widget.active_payload == "second payload"


def test_read_only_still_allows_programmatic_selection(qapp: QApplication) -> None:
    """Allow programmatic selection in read-only mode."""
    widget = VariantWidget(_create_variants(), initial_index=0, read_only=True)

    widget.set_active_variant(2)

    assert widget.active_index == 2
    assert widget.active_payload == "third payload"


def test_payloads_preserve_variant_order(qapp: QApplication) -> None:
    """Return all payloads in variant order."""
    widget = VariantWidget(_create_variants())

    assert widget.payloads == ("first payload", "second payload", "third payload")


def test_active_payload_matches_selected_variant(qapp: QApplication) -> None:
    """Return the payload belonging to the active variant."""
    widget = VariantWidget(_create_variants(), initial_index=0)

    assert widget.active_payload == "first payload"

    widget.set_active_variant(2)

    assert widget.active_payload == "third payload"


def test_can_switch_between_variants_multiple_times(qapp: QApplication) -> None:
    """Allow repeated changes of the active variant."""
    widget = VariantWidget(_create_variants())

    widget.set_active_variant(0)

    assert widget.active_index == 0
    assert widget.active_payload == "first payload"

    widget.set_active_variant(2)

    assert widget.active_index == 2
    assert widget.active_payload == "third payload"

    widget.set_active_variant(1)

    assert widget.active_index == 1
    assert widget.active_payload == "second payload"


def test_requires_at_least_one_variant(qapp: QApplication) -> None:
    """Reject an empty variant collection."""
    with pytest.raises(ValueError, match="VariantWidget requires at least one variant"):
        VariantWidget([])


def test_set_active_variant_rejects_non_integer_index(qapp: QApplication) -> None:
    """Reject a non-integer variant index."""
    widget = VariantWidget(_create_variants())

    with pytest.raises(TypeError, match="Variant index must be an integer"):
        widget.set_active_variant("1")  # type: ignore[arg-type]


def test_set_active_variant_rejects_boolean_index(qapp: QApplication) -> None:
    """Reject boolean values as variant indices."""
    widget = VariantWidget(_create_variants())

    with pytest.raises(TypeError, match="Variant index must be an integer"):
        widget.set_active_variant(True)  # type: ignore[arg-type]


def test_set_active_variant_rejects_negative_index(qapp: QApplication) -> None:
    """Reject a negative variant index."""
    widget = VariantWidget(_create_variants())

    with pytest.raises(IndexError, match="Variant index out of range"):
        widget.set_active_variant(-1)


def test_set_active_variant_rejects_index_after_last_variant(qapp: QApplication) -> None:
    """Reject an index outside the available variants."""
    widget = VariantWidget(_create_variants())

    with pytest.raises(IndexError, match="Variant index out of range"):
        widget.set_active_variant(3)


def test_initial_index_uses_index_validation(qapp: QApplication) -> None:
    """Validate the initial index during construction."""
    with pytest.raises(IndexError, match="Variant index out of range"):
        VariantWidget(_create_variants(), initial_index=3)


def test_initial_index_rejects_non_integer_value(qapp: QApplication) -> None:
    """Reject a noninteger initial index."""
    with pytest.raises(TypeError, match="Variant index must be an integer"):
        VariantWidget(_create_variants(), initial_index="1")  # type: ignore[arg-type]


def test_stacked_widget_size_hint_uses_current_page(qapp: QApplication) -> None:
    """Return the size hint of the current page."""
    first_page = SizedWidget(QSize(100, 50))
    second_page = SizedWidget(QSize(200, 80))

    widget = _VariantStackedWidget()
    widget.addWidget(first_page)
    widget.addWidget(second_page)

    widget.setCurrentIndex(0)

    assert widget.sizeHint() == QSize(100, 50)

    widget.setCurrentIndex(1)

    assert widget.sizeHint() == QSize(200, 80)


def test_stacked_widget_minimum_size_hint_uses_current_page(qapp: QApplication) -> None:
    """Return the minimum size hint of the current page."""
    first_page = SizedWidget(QSize(80, 40))
    second_page = SizedWidget(QSize(150, 60))

    widget = _VariantStackedWidget()
    widget.addWidget(first_page)
    widget.addWidget(second_page)

    widget.setCurrentIndex(0)

    assert widget.minimumSizeHint() == QSize(80, 40)

    widget.setCurrentIndex(1)

    assert widget.minimumSizeHint() == QSize(150, 60)
