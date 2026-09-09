from orebiters_modding_tool.app.widgets.dynamic_combo_box import DynamicComboBox


def test_loads_choices_on_creation(qapp: object) -> None:
    """Load choices when the combo box is created."""
    combo = DynamicComboBox(lambda _current_value: ("first", "second", "third"))

    assert combo.count() == 3
    assert combo.itemData(0) == "first"
    assert combo.itemData(1) == "second"
    assert combo.itemData(2) == "third"


def test_does_not_select_first_choice_automatically(qapp: object) -> None:
    """Keep the combo box empty when no choice was selected."""
    combo = DynamicComboBox(lambda _current_value: ("first", "second", "third"))

    assert combo.currentIndex() == -1
    assert combo.currentData() is None


def test_refreshes_choices_when_popup_is_shown(qapp: object) -> None:
    """Refresh choices before showing the popup."""
    choices = ["first", "second"]

    combo = DynamicComboBox(lambda _current_value: choices)

    assert combo.count() == 2

    choices.append("third")

    combo.showPopup()
    combo.hidePopup()

    assert combo.count() == 3
    assert combo.itemData(2) == "third"


def test_preserves_current_choice_when_refreshing(qapp: object) -> None:
    """Preserve the current choice when it remains available."""
    choices = ["first", "second", "third"]
    combo = DynamicComboBox(lambda _current_value: choices)

    combo.setCurrentIndex(1)

    choices.append("fourth")

    combo.showPopup()
    combo.hidePopup()

    assert combo.currentData() == "second"
    assert combo.count() == 4


def test_clears_current_choice_when_it_is_no_longer_available(qapp: object) -> None:
    """Clear the current choice when it is no longer available."""
    choices = ["first", "second", "third"]
    combo = DynamicComboBox(lambda _current_value: choices)

    combo.setCurrentIndex(1)

    choices.remove("second")

    combo.showPopup()
    combo.hidePopup()

    assert combo.currentIndex() == -1
    assert combo.currentData() is None
