from dataclasses import dataclass, field
from enum import Enum

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QWidget,
)

from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget
from orebiters_modding_tool.app.editors.editor_field import (
    EditorField,
    EditorVariant,
    EditorVariantField,
)
from orebiters_modding_tool.app.widgets.dictionary_widget import DictionaryWidget
from orebiters_modding_tool.app.widgets.dynamic_combo_box import DynamicComboBox
from orebiters_modding_tool.app.widgets.list_widget import ListWidget
from orebiters_modding_tool.app.widgets.variant_widget import VariantWidget


class SampleEnum(Enum):
    """Enum used for BaseEditorWidget tests."""

    FIRST = "first"
    SECOND = "second"


@dataclass
class SampleItem:
    """Simple item used for BaseEditorWidget tests."""

    # String value used to test QLineEdit fields.
    text: str = "Test text"

    # Integer value used to test QSpinBox fields.
    number: int = 42

    # Floating-point value used to test QDoubleSpinBox fields.
    decimal: float = 3.14

    # Boolean value used to test QCheckBox fields.
    enabled: bool = True

    # Enum value used to test enum QComboBox fields.
    enum_value: SampleEnum = SampleEnum.FIRST

    # Optional value used to test empty and read-only fields.
    optional_value: object | None = None

    # Optional numeric values used to test optional numeric fields.
    optional_number: int | None = None

    # Optional floating-point value used to test optional numeric fields.
    optional_decimal: float | None = None

    # List value used to test ListEditorWidget fields.
    values: list[object] = field(default_factory=list)

    # Typed list value used to test ListEditorWidget fields.
    typed_values: list[str] = field(default_factory=list)

    # Dictionary value used to test DictionaryEditorWidget fields.
    mapping: dict[object, object] = field(default_factory=dict)


@dataclass
class VariantItem:
    """Item used for variant editor tests."""

    text: str | None = None
    number: int | None = None
    description: str | None = None


class UnsupportedValue:
    """Unsupported value type used for tests."""


@dataclass
class UnsupportedItem:
    """Item containing an unsupported field value."""

    value: UnsupportedValue


class EmptyEditorWidget(BaseEditorWidget[object]):
    """Minimal editor used for custom editor tests."""

    FIELDS = ()


class BasicFieldsEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor containing basic field types."""

    FIELDS = (
        EditorField(name="text", label="Text"),
        EditorField(name="number", label="Number"),
        EditorField(name="decimal", label="Decimal"),
        EditorField(name="enabled", label="Enabled"),
        EditorField(name="enum_value", label="Enum"),
        EditorField(name="optional_value", label="Optional"),
    )


class OptionalNumberEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor containing optional numeric fields."""

    FIELDS = (
        EditorField(
            name="optional_number",
            label="Number",
            value_type=int | None,
        ),
        EditorField(
            name="optional_decimal",
            label="Decimal",
            value_type=float | None,
        ),
    )


class ValueProviderEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor used for value provider tests."""

    FIELDS = (
        EditorField(
            name="provided_value",
            label="Provided Value",
            value_provider=lambda editor: f"Provided: {editor.item.text}",
        ),
    )


class ChoiceEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor used for choice field tests."""

    FIELDS = (
        EditorField(
            name="text",
            label="Text",
            choices_provider=lambda _editor, _current_value: ("first", "second", "third"),
            choice_formatter=lambda choice: str(choice).upper(),
        ),
    )


class CustomEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor containing a custom editor field."""

    FIELDS = (
        EditorField(
            name="text",
            label="Text",
            editor_widget_type=EmptyEditorWidget,
        ),
    )


class ListEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor containing a list field."""

    FIELDS = (
        EditorField(
            name="values",
            label="Values",
            item_factory=lambda _context: "new value",
        ),
    )


class TypedListEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor containing a typed list without an item factory."""

    FIELDS = (
        EditorField(
            name="typed_values",
            label="Typed Values",
        ),
    )


class ReadOnlyListEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor containing a read-only list field."""

    FIELDS = (
        EditorField(
            name="values",
            label="Values",
            read_only=True,
            item_factory=lambda _context: "new value",
        ),
    )


class DictionaryEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor containing a dictionary field."""

    FIELDS = (
        EditorField(
            name="mapping",
            label="Mapping",
            editor_widget_type=EmptyEditorWidget,
        ),
    )


class NestedItemEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor used to test nested editor saving."""

    FIELDS = (EditorField(name="text", label="Text"),)


class NestedDictionaryEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor used to test dictionary saving."""

    FIELDS = (
        EditorField(
            name="mapping",
            label="Mapping",
            editor_widget_type=NestedItemEditorWidget,
        ),
    )


class ReadOnlyEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor containing a field-level read-only value."""

    FIELDS = (
        EditorField(
            name="text",
            label="Text",
            read_only=True,
        ),
    )


class SectionEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor used for section layout tests."""

    FIELDS = (
        EditorField(
            name="text",
            label="Text",
        ),
        EditorField(
            name="values",
            label="Values",
            item_factory=lambda _context: "new value",
        ),
        EditorField(
            name="number",
            label="Number",
        ),
        EditorField(
            name="mapping",
            label="Mapping",
            editor_widget_type=EmptyEditorWidget,
        ),
    )


class UnsupportedEditorWidget(BaseEditorWidget[UnsupportedItem]):
    """Editor containing an unsupported field."""

    FIELDS = (EditorField(name="value", label="Value"),)


class NestedListEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor containing a list whose items are lists."""

    FIELDS = (
        EditorField(
            name="values",
            label="Values",
            item_factory=lambda _context: [],
        ),
    )


class VariantEditorWidget(BaseEditorWidget[VariantItem]):
    """Editor containing two simple variants."""

    FIELDS = (
        EditorVariantField(
            label="Variant",
            variants=(
                EditorVariant(
                    label="Text",
                    fields=(
                        EditorField(
                            name="text",
                            label="Text",
                        ),
                    ),
                ),
                EditorVariant(
                    label="Number",
                    fields=(
                        EditorField(
                            name="number",
                            label="Number",
                        ),
                    ),
                ),
            ),
        ),
    )


class MultiFieldVariantEditorWidget(BaseEditorWidget[VariantItem]):
    """Editor containing variants with multiple fields."""

    FIELDS = (
        EditorVariantField(
            label="Variant",
            variants=(
                EditorVariant(
                    label="Text",
                    fields=(
                        EditorField(
                            name="text",
                            label="Text",
                        ),
                        EditorField(
                            name="description",
                            label="Description",
                        ),
                    ),
                ),
                EditorVariant(
                    label="Number",
                    fields=(
                        EditorField(
                            name="number",
                            label="Number",
                        ),
                    ),
                ),
            ),
        ),
    )


class ReadOnlyVariantEditorWidget(BaseEditorWidget[VariantItem]):
    """Editor containing a read-only variant field."""

    FIELDS = (
        EditorVariantField(
            label="Variant",
            read_only=True,
            variants=(
                EditorVariant(
                    label="Text",
                    fields=(
                        EditorField(
                            name="text",
                            label="Text",
                        ),
                    ),
                ),
                EditorVariant(
                    label="Number",
                    fields=(
                        EditorField(
                            name="number",
                            label="Number",
                        ),
                    ),
                ),
            ),
        ),
    )


class ReadOnlyVariantFieldEditorWidget(BaseEditorWidget[VariantItem]):
    """Editor containing a read-only field inside a variant."""

    FIELDS = (
        EditorVariantField(
            label="Variant",
            variants=(
                EditorVariant(
                    label="Text",
                    fields=(
                        EditorField(
                            name="text",
                            label="Text",
                            read_only=True,
                        ),
                    ),
                ),
                EditorVariant(
                    label="Number",
                    fields=(
                        EditorField(
                            name="number",
                            label="Number",
                        ),
                    ),
                ),
            ),
        ),
    )


class NestedVariantEditorWidget(BaseEditorWidget[VariantItem]):
    """Editor containing a nested editor inside a variant."""

    FIELDS = (
        EditorVariantField(
            label="Variant",
            variants=(
                EditorVariant(
                    label="Text",
                    fields=(
                        EditorField(
                            name="text",
                            label="Text",
                            editor_widget_type=EmptyEditorWidget,
                        ),
                    ),
                ),
            ),
        ),
    )


def _get_variant_widget(editor: BaseEditorWidget) -> VariantWidget:
    """Return the VariantWidget created by an editor."""
    widget = editor.findChild(VariantWidget)

    assert widget is not None

    return widget


# ============================================================================
# Basic fields
# ============================================================================


@pytest.mark.parametrize(
    ("field_name", "widget_type", "value"),
    [
        ("text", QLineEdit, "Test text"),
        ("number", QSpinBox, 42),
        ("decimal", QDoubleSpinBox, 3.14),
        ("enabled", QCheckBox, True),
    ],
)
def test_creates_basic_field(
    qapp: QApplication,
    field_name: str,
    widget_type: type[QWidget],
    value: object,
) -> None:
    """Create editors for supported basic value types."""
    editor = BasicFieldsEditorWidget(SampleItem())

    field = editor._get_field_widget(field_name)

    assert isinstance(field, widget_type)

    match field:
        case QLineEdit():
            assert field.text() == value
        case QSpinBox():
            assert field.value() == value
        case QDoubleSpinBox():
            assert field.value() == value
        case QCheckBox():
            assert field.isChecked() == value


def test_item_returns_edited_item(qapp: QApplication) -> None:
    """Return the item being edited."""
    item = SampleItem()

    editor = BasicFieldsEditorWidget(item)

    assert editor.item is item


def test_creates_enum_field(qapp: QApplication) -> None:
    """Create a combo box for enum values."""
    editor = BasicFieldsEditorWidget(SampleItem())

    field = editor._get_field_widget("enum_value")

    assert isinstance(field, QComboBox)
    assert field.count() == len(SampleEnum)
    assert field.currentData() is SampleEnum.FIRST

    assert field.itemText(0) == "FIRST"
    assert field.itemData(0) is SampleEnum.FIRST
    assert field.itemText(1) == "SECOND"
    assert field.itemData(1) is SampleEnum.SECOND


def test_creates_empty_field_for_none_value(qapp: QApplication) -> None:
    """Create an empty line edit for an untyped None value."""
    editor = BasicFieldsEditorWidget(SampleItem(optional_value=None))

    field = editor._get_field_widget("optional_value")

    assert isinstance(field, QLineEdit)
    assert field.text() == ""


def test_creates_optional_number_fields(qapp: QApplication) -> None:
    """Create line edits for optional numeric fields."""
    editor = OptionalNumberEditorWidget(SampleItem())

    number_field = editor._get_field_widget("optional_number")
    decimal_field = editor._get_field_widget("optional_decimal")

    assert isinstance(number_field, QLineEdit)
    assert isinstance(decimal_field, QLineEdit)

    assert number_field.text() == ""
    assert decimal_field.text() == ""


# ============================================================================
# Value providers and choices
# ============================================================================


def test_uses_value_provider(qapp: QApplication) -> None:
    """Use a configured value provider instead of an item attribute."""
    item = SampleItem(text="Custom text")

    editor = ValueProviderEditorWidget(item)

    field = editor._get_field_widget("provided_value")

    assert isinstance(field, QLineEdit)
    assert field.text() == "Provided: Custom text"


def test_creates_choice_field(qapp: QApplication) -> None:
    """Create a combo box from configured choices."""
    editor = ChoiceEditorWidget(SampleItem(text="second"))

    field = editor._get_field_widget("text")

    assert isinstance(field, DynamicComboBox)
    assert field.count() == 3
    assert field.currentData() == "second"
    assert field.currentText() == "SECOND"

    assert field.itemText(0) == "FIRST"
    assert field.itemText(1) == "SECOND"
    assert field.itemText(2) == "THIRD"


def test_choice_field_raises_without_provider(qapp: QApplication) -> None:
    """Raise an error when choice creation has no provider."""
    editor = BasicFieldsEditorWidget(SampleItem())

    field_config = EditorField(name="text", label="Text")

    with pytest.raises(ValueError, match="Choice field 'text' requires a choices provider."):
        editor._create_choice_field(field_config, "Test")


# ============================================================================
# Read-only and custom editors
# ============================================================================


@pytest.mark.parametrize(
    ("value", "expected_text"),
    [
        ("Text", "Text"),
        (123, "123"),
        (3.14, "3.14"),
        (True, "True"),
        (None, "-"),
    ],
)
def test_creates_read_only_field(qapp: QApplication, value: object, expected_text: str) -> None:
    """Create selectable labels for read-only values."""
    editor = EmptyEditorWidget(object())

    field = editor._create_read_only_field(value)

    assert isinstance(field, QLabel)
    assert field.text() == expected_text
    assert field.textInteractionFlags() & Qt.TextInteractionFlag.TextSelectableByMouse


def test_field_level_read_only_uses_label(qapp: QApplication) -> None:
    """Use a read-only label for a read-only field."""
    editor = ReadOnlyEditorWidget(SampleItem())

    field = editor._get_field_widget("text")

    assert isinstance(field, QLabel)
    assert field.text() == "Test text"


@pytest.mark.parametrize(
    "field_name",
    [
        "text",
        "number",
        "decimal",
        "enabled",
        "enum_value",
        "optional_value",
    ],
)
def test_editor_read_only_overrides_all_basic_fields(qapp: QApplication, field_name: str) -> None:
    """Use read-only widgets when the whole editor is read-only."""
    editor = BasicFieldsEditorWidget(SampleItem(), read_only=True)

    field = editor._get_field_widget(field_name)

    assert isinstance(field, QLabel)


def test_creates_custom_editor_widget(qapp: QApplication) -> None:
    """Create a configured custom editor widget."""
    editor = CustomEditorWidget(SampleItem())

    field = editor._get_field_widget("text")

    assert isinstance(field, EmptyEditorWidget)


def test_passes_context_to_custom_editor(qapp: QApplication) -> None:
    """Pass shared context to custom editor widgets."""
    context = {"test_key": "test_value"}

    editor = CustomEditorWidget(SampleItem(), context=context)

    field = editor._get_field_widget("text")

    assert isinstance(field, EmptyEditorWidget)
    assert field._context is context


def test_passes_read_only_to_custom_editor(qapp: QApplication) -> None:
    """Pass read-only state to custom editor widgets."""
    editor = CustomEditorWidget(SampleItem(), read_only=True)

    field = editor._get_field_widget("text")

    assert isinstance(field, EmptyEditorWidget)
    assert field._read_only is True


# ============================================================================
# Lists
# ============================================================================


def test_creates_list_field(qapp: QApplication) -> None:
    """Create a ListWidget for list values."""
    editor = ListEditorWidget(SampleItem(values=["first", "second"]))

    field = editor._get_field_widget("values")

    assert isinstance(field, ListWidget)


def test_list_items_use_declared_runtime_type(qapp: QApplication) -> None:
    """Create list item editors using the existing item type."""
    editor = ListEditorWidget(SampleItem(values=["first"]))

    field = editor._get_field_widget("values")

    assert isinstance(field, ListWidget)

    item_widget = field._item_widgets[0]

    assert isinstance(item_widget, QLineEdit)
    assert item_widget.text() == "first"


def test_list_field_creates_default_item_from_annotation(qapp: QApplication) -> None:
    """Create a default list item from the model annotation."""
    editor = TypedListEditorWidget(SampleItem())

    field = editor._get_field_widget("typed_values")

    assert isinstance(field, ListWidget)

    field._add_button.click()

    assert field.item_count() == 1

    item_widget = field.item_at(0)

    assert isinstance(item_widget, QLineEdit)
    assert item_widget.text() == ""


def test_list_item_factory_overrides_annotation_default(qapp: QApplication) -> None:
    """Use the configured item factory instead of the annotation default."""
    editor = ListEditorWidget(SampleItem())

    field = editor._get_field_widget("values")

    assert isinstance(field, ListWidget)

    field._add_button.click()

    item_widget = field.item_at(0)

    assert isinstance(item_widget, QLineEdit)
    assert item_widget.text() == "new value"


def test_list_field_passes_context_to_item_factory(qapp: QApplication) -> None:
    """Pass editor context to the list item factory."""
    context = {"test": "value"}

    class ContextListEditorWidget(BaseEditorWidget[SampleItem]):
        """Editor used for list factory context tests."""

        FIELDS = (
            EditorField(
                name="values",
                label="Values",
                item_factory=lambda item_context: item_context["test"],
            ),
        )

    editor = ContextListEditorWidget(SampleItem(), context=context)

    field = editor._get_field_widget("values")

    assert isinstance(field, ListWidget)

    field._add_button.click()

    item_widget = field.item_at(0)

    assert isinstance(item_widget, QLineEdit)
    assert item_widget.text() == "value"


def test_nested_list_item_raises_error(qapp: QApplication) -> None:
    """Reject nested list values."""
    with pytest.raises(ValueError, match="Nested lists are not supported."):
        NestedListEditorWidget(SampleItem(values=[["nested"]]))


def test_read_only_list_disables_add_and_remove_operations(qapp: QApplication) -> None:
    """Disable list modifications in a read-only editor."""
    editor = ListEditorWidget(SampleItem(values=["first"]), read_only=True)

    field = editor._get_field_widget("values")

    assert isinstance(field, ListWidget)
    assert not field._add_button.isEnabled()
    assert all(not button.isEnabled() for button in field._remove_buttons)


def test_field_level_read_only_disables_list_operations(qapp: QApplication) -> None:
    """Disable list modifications for a read-only list field."""
    editor = ReadOnlyListEditorWidget(SampleItem(values=["first"]))

    field = editor._get_field_widget("values")

    assert isinstance(field, ListWidget)
    assert not field._add_button.isEnabled()
    assert all(not button.isEnabled() for button in field._remove_buttons)


# ============================================================================
# Dictionaries and nested editors
# ============================================================================


def test_creates_dictionary_field(qapp: QApplication) -> None:
    """Create a DictionaryWidget for dictionary values."""
    editor = DictionaryEditorWidget(SampleItem(mapping={"first": object(), "second": object()}))

    field = editor._get_field_widget("mapping")

    assert isinstance(field, DictionaryWidget)


def test_dictionary_field_creates_widgets_for_all_items(qapp: QApplication) -> None:
    """Create an item widget for every dictionary value."""
    editor = DictionaryEditorWidget(SampleItem(mapping={"first": object(), "second": object()}))

    field = editor._get_field_widget("mapping")

    assert isinstance(field, DictionaryWidget)
    assert set(field._item_widgets) == {"first", "second"}

    assert isinstance(field._item_widgets["first"], EmptyEditorWidget)
    assert isinstance(field._item_widgets["second"], EmptyEditorWidget)


def test_dictionary_field_passes_context(qapp: QApplication) -> None:
    """Pass shared context to dictionary item editors."""
    context = {"language": "en"}

    editor = DictionaryEditorWidget(SampleItem(mapping={"first": object()}), context=context)

    field = editor._get_field_widget("mapping")

    assert isinstance(field, DictionaryWidget)

    nested_editor = field._item_widgets["first"]

    assert isinstance(nested_editor, EmptyEditorWidget)
    assert nested_editor._context is context


def test_dictionary_field_passes_read_only_state(qapp: QApplication) -> None:
    """Pass read-only state to dictionary item editors."""
    editor = DictionaryEditorWidget(SampleItem(mapping={"first": object()}), read_only=True)

    field = editor._get_field_widget("mapping")

    assert isinstance(field, DictionaryWidget)

    nested_editor = field._item_widgets["first"]

    assert isinstance(nested_editor, EmptyEditorWidget)
    assert nested_editor._read_only is True


def test_nested_dictionary_item_raises_error(qapp: QApplication) -> None:
    """Reject nested dictionary values."""
    editor = EmptyEditorWidget(object())

    with pytest.raises(ValueError, match="Nested dictionaries are not supported."):
        editor._create_dict_item_field(EditorField(name="mapping", label="Mapping"), {})


def test_nested_dictionary_editor_is_created(qapp: QApplication) -> None:
    """Create nested editors for dictionary values."""
    first_value = SampleItem(text="first")

    editor = NestedDictionaryEditorWidget(SampleItem(mapping={"first": first_value}))

    field = editor._get_field_widget("mapping")

    assert isinstance(field, DictionaryWidget)

    nested_editor = field._item_widgets["first"]

    assert isinstance(nested_editor, NestedItemEditorWidget)


def test_nested_dictionary_editor_does_not_have_save_button(qapp: QApplication) -> None:
    """Do not create save buttons for nested dictionary editors."""
    editor = NestedDictionaryEditorWidget(SampleItem(mapping={"first": SampleItem(text="first")}))

    field = editor._get_field_widget("mapping")

    assert isinstance(field, DictionaryWidget)

    nested_editor = field._item_widgets["first"]

    assert isinstance(nested_editor, NestedItemEditorWidget)
    assert not hasattr(nested_editor, "_save_button")


# ============================================================================
# Layout
# ============================================================================


def test_creates_multiple_editor_sections(qapp: QApplication) -> None:
    """Split simple and complex fields into separate form sections."""
    editor = SectionEditorWidget(SampleItem(values=["first"], mapping={"key": object()}))

    layout = editor._layout

    form_layouts = [
        layout.itemAt(index).layout()
        for index in range(layout.count())
        if layout.itemAt(index).layout() is not None
        and isinstance(layout.itemAt(index).layout(), QFormLayout)
    ]

    assert len(form_layouts) == 2


def test_complex_field_labels_are_bold(qapp: QApplication) -> None:
    """Display complex field labels using bold text."""
    editor = SectionEditorWidget(SampleItem())

    labels = [
        editor._layout.itemAt(index).widget()
        for index in range(editor._layout.count())
        if isinstance(editor._layout.itemAt(index).widget(), QLabel)
    ]

    assert any(label.text() == "Values" and label.font().bold() for label in labels)
    assert any(label.text() == "Mapping" and label.font().bold() for label in labels)


def test_adds_spacing_between_editor_sections(qapp: QApplication) -> None:
    """Add spacing between separate editor sections."""
    editor = SectionEditorWidget(SampleItem())

    spacings = [
        editor._layout.itemAt(index)
        for index in range(editor._layout.count())
        if editor._layout.itemAt(index).spacerItem() is not None
    ]

    assert len(spacings) >= 3


# ============================================================================
# Unsupported values and widget types
# ============================================================================


def test_unsupported_value_raises_error(qapp: QApplication) -> None:
    """Raise an error for unsupported field values."""
    with pytest.raises(ValueError, match="Unsupported field type: UnsupportedValue."):
        UnsupportedEditorWidget(UnsupportedItem(value=UnsupportedValue()))


def test_get_base_widget_value_raises_for_unsupported_widget(qapp: QApplication) -> None:
    """Raise an error for unsupported editor widgets."""
    editor = EmptyEditorWidget(object())

    with pytest.raises(ValueError, match="Unsupported editor widget type: QWidget."):
        editor._get_base_widget_value(QWidget())


# ============================================================================
# Context
# ============================================================================


def test_default_context_is_empty_dictionary(qapp: QApplication) -> None:
    """Use an empty dictionary when no context is provided."""
    editor = BasicFieldsEditorWidget(SampleItem())

    assert editor._context == {}


def test_preserves_provided_context(qapp: QApplication) -> None:
    """Preserve the provided context object."""
    context = {"key": "value"}

    editor = BasicFieldsEditorWidget(SampleItem(), context=context)

    assert editor._context is context


# ============================================================================
# Saving
# ============================================================================


def test_save_updates_basic_field_values(qapp: QApplication) -> None:
    """Save modified basic field values to the edited item."""
    item = SampleItem()

    editor = BasicFieldsEditorWidget(item)

    text_field = editor._get_field_widget("text")
    number_field = editor._get_field_widget("number")
    decimal_field = editor._get_field_widget("decimal")
    enabled_field = editor._get_field_widget("enabled")
    enum_field = editor._get_field_widget("enum_value")
    optional_field = editor._get_field_widget("optional_value")

    assert isinstance(text_field, QLineEdit)
    assert isinstance(number_field, QSpinBox)
    assert isinstance(decimal_field, QDoubleSpinBox)
    assert isinstance(enabled_field, QCheckBox)
    assert isinstance(enum_field, QComboBox)
    assert isinstance(optional_field, QLineEdit)

    text_field.setText("Updated text")
    number_field.setValue(123)
    decimal_field.setValue(6.28)
    enabled_field.setChecked(False)
    enum_field.setCurrentIndex(1)
    optional_field.setText("Optional value")

    editor.save()

    assert item.text == "Updated text"
    assert item.number == 123
    assert item.decimal == 6.28
    assert item.enabled is False
    assert item.enum_value is SampleEnum.SECOND
    assert item.optional_value == "Optional value"


def test_save_converts_optional_numeric_values(qapp: QApplication) -> None:
    """Convert optional numeric line-edit values to their declared types."""
    item = SampleItem()

    editor = OptionalNumberEditorWidget(item)

    number_field = editor._get_field_widget("optional_number")
    decimal_field = editor._get_field_widget("optional_decimal")

    assert isinstance(number_field, QLineEdit)
    assert isinstance(decimal_field, QLineEdit)

    number_field.setText("123")
    decimal_field.setText("4.5")

    editor.save()

    assert item.optional_number == 123
    assert item.optional_decimal == 4.5


def test_save_converts_empty_optional_numeric_values_to_none(qapp: QApplication) -> None:
    """Convert empty optional numeric fields to None."""
    item = SampleItem(
        optional_number=123,
        optional_decimal=4.5,
    )

    editor = OptionalNumberEditorWidget(item)

    number_field = editor._get_field_widget("optional_number")
    decimal_field = editor._get_field_widget("optional_decimal")

    assert isinstance(number_field, QLineEdit)
    assert isinstance(decimal_field, QLineEdit)

    number_field.clear()
    decimal_field.clear()

    editor.save()

    assert item.optional_number is None
    assert item.optional_decimal is None


def test_save_rejects_invalid_optional_numeric_value(qapp: QApplication) -> None:
    """Reject invalid numeric input during save."""
    editor = OptionalNumberEditorWidget(SampleItem())

    field = editor._get_field_widget("optional_number")

    assert isinstance(field, QLineEdit)

    field.setText("not a number")

    with pytest.raises(ValueError, match="Invalid int value"):
        editor.save()


def test_save_does_not_partially_update_item_when_validation_fails(qapp: QApplication) -> None:
    """Keep the model unchanged when saving fails."""
    item = SampleItem(text="Original", optional_number=10)

    class Editor(BaseEditorWidget[SampleItem]):
        """Editor used to test atomic saving."""

        FIELDS = (
            EditorField(name="text", label="Text"),
            EditorField(name="optional_number", label="Number", value_type=int | None),
        )

    editor = Editor(item)

    text_field = editor._get_field_widget("text")
    number_field = editor._get_field_widget("optional_number")

    assert isinstance(text_field, QLineEdit)
    assert isinstance(number_field, QLineEdit)

    text_field.setText("Changed")
    number_field.setText("invalid")

    with pytest.raises(ValueError):
        editor.save()

    assert item.text == "Original"
    assert item.optional_number == 10


def test_save_updates_choice_field_value(qapp: QApplication) -> None:
    """Save the currently selected choice value."""
    item = SampleItem(text="first")

    editor = ChoiceEditorWidget(item)

    field = editor._get_field_widget("text")

    assert isinstance(field, DynamicComboBox)

    field.showPopup()
    field.hidePopup()

    assert field.count() == 3

    field.setCurrentIndex(2)

    editor.save()

    assert item.text == "third"


def test_save_does_not_save_field_level_read_only_value(qapp: QApplication) -> None:
    """Do not save values from field-level read-only fields."""
    item = SampleItem(text="Original text")

    editor = ReadOnlyEditorWidget(item)

    field = editor._get_field_widget("text")

    assert isinstance(field, QLabel)

    field.setText("Modified text")

    editor.save()

    assert item.text == "Original text"


def test_save_does_not_modify_value_provider_value(qapp: QApplication) -> None:
    """Do not save values provided by a value provider."""
    item = SampleItem(text="Original text")

    editor = ValueProviderEditorWidget(item)

    field = editor._get_field_widget("provided_value")

    assert isinstance(field, QLineEdit)

    field.setText("Modified value")

    editor.save()

    assert item.text == "Original text"


def test_save_updates_list_values(qapp: QApplication) -> None:
    """Save modified list item values."""
    item = SampleItem(values=["first", "second"])

    editor = ListEditorWidget(item)

    field = editor._get_field_widget("values")

    assert isinstance(field, ListWidget)

    first_item_widget = field.item_at(0)
    second_item_widget = field.item_at(1)

    assert isinstance(first_item_widget, QLineEdit)
    assert isinstance(second_item_widget, QLineEdit)

    first_item_widget.setText("updated first")
    second_item_widget.setText("updated second")

    editor.save()

    assert item.values == ["updated first", "updated second"]


def test_save_updates_nested_dictionary_values(qapp: QApplication) -> None:
    """Save changes made by nested dictionary editors."""
    first_value = SampleItem(text="first")
    second_value = SampleItem(text="second")

    item = SampleItem(
        mapping={
            "first": first_value,
            "second": second_value,
        },
    )

    editor = NestedDictionaryEditorWidget(item)

    field = editor._get_field_widget("mapping")

    assert isinstance(field, DictionaryWidget)

    first_editor = field._item_widgets["first"]
    second_editor = field._item_widgets["second"]

    assert isinstance(first_editor, NestedItemEditorWidget)
    assert isinstance(second_editor, NestedItemEditorWidget)

    first_text_widget = first_editor._get_field_widget("text")
    second_text_widget = second_editor._get_field_widget("text")

    assert isinstance(first_text_widget, QLineEdit)
    assert isinstance(second_text_widget, QLineEdit)

    first_text_widget.setText("updated first")
    second_text_widget.setText("updated second")

    editor.save()

    assert item.mapping == {
        "first": first_value,
        "second": second_value,
    }
    assert first_value.text == "updated first"
    assert second_value.text == "updated second"


def test_save_emits_saved_signal(qapp: QApplication) -> None:
    """Emit the saved signal after saving."""
    editor = BasicFieldsEditorWidget(SampleItem())

    saved_emissions: list[None] = []

    editor.saved.connect(lambda: saved_emissions.append(None))

    editor.save()

    assert len(saved_emissions) == 1


# ============================================================================
# Save button
# ============================================================================


def test_creates_save_button_by_default(qapp: QApplication) -> None:
    """Create a save button by default."""
    editor = BasicFieldsEditorWidget(SampleItem())

    assert isinstance(editor._save_button, QPushButton)
    assert not editor._save_button.isVisible()

    editor.show()

    assert editor._save_button.isVisible()


def test_does_not_create_save_button_when_hidden(qapp: QApplication) -> None:
    """Do not create a save button when disabled."""
    editor = BasicFieldsEditorWidget(SampleItem(), show_save_button=False)

    assert not hasattr(editor, "_save_button")


def test_does_not_create_save_button_for_read_only_editor(qapp: QApplication) -> None:
    """Do not create a save button for a read-only editor."""
    editor = BasicFieldsEditorWidget(SampleItem(), read_only=True)

    assert not hasattr(editor, "_save_button")


def test_clicking_save_button_saves_editor_values(qapp: QApplication) -> None:
    """Save editor values when the save button is clicked."""
    item = SampleItem(text="Original text")

    editor = BasicFieldsEditorWidget(item)

    field = editor._get_field_widget("text")

    assert isinstance(field, QLineEdit)

    field.setText("Updated text")

    editor._save_button.click()

    assert item.text == "Updated text"


def test_nested_custom_editor_does_not_show_save_button(qapp: QApplication) -> None:
    """Do not show a save button inside nested custom editors."""
    editor = CustomEditorWidget(SampleItem())

    field = editor._get_field_widget("text")

    assert isinstance(field, EmptyEditorWidget)
    assert not hasattr(field, "_save_button")


# ============================================================================
# Refresh
# ============================================================================


def test_refresh_updates_nested_list_editors(qapp: QApplication) -> None:
    """Refresh nested list editors recursively."""
    can_add = False

    class Editor(BaseEditorWidget[SampleItem]):
        FIELDS = (
            EditorField(
                name="values",
                label="Values",
                item_factory=lambda _context: "new value",
                can_add_provider=lambda _editor: can_add,
            ),
        )

    editor = Editor(SampleItem(values=["first"]))

    field = editor._get_field_widget("values")

    assert isinstance(field, ListWidget)
    assert not field._add_button.isEnabled()

    can_add = True

    editor.refresh()

    assert field._add_button.isEnabled()


def test_refresh_updates_nested_dictionary_editors(qapp: QApplication) -> None:
    """Refresh nested dictionary editors recursively."""
    refresh_count = 0

    class RefreshableEditor(BaseEditorWidget[SampleItem]):
        """Nested editor used to observe refresh."""

        FIELDS = ()

        def refresh(self) -> None:
            nonlocal refresh_count

            refresh_count += 1

    class Editor(BaseEditorWidget[SampleItem]):
        """Editor containing nested dictionary editors."""

        FIELDS = (
            EditorField(
                name="mapping",
                label="Mapping",
                editor_widget_type=RefreshableEditor,
            ),
        )

    editor = Editor(SampleItem(mapping={"first": SampleItem(), "second": SampleItem()}))

    editor.refresh()

    assert refresh_count == 2


# ============================================================================
# Variants
# ============================================================================


def test_creates_variant_field(qapp: QApplication) -> None:
    """Create a VariantWidget for an EditorVariantField."""
    editor = VariantEditorWidget(VariantItem())

    widget = _get_variant_widget(editor)

    assert isinstance(widget, VariantWidget)
    assert len(widget.payloads) == 2


def test_variant_field_has_no_active_variant_when_no_fields_are_populated(
    qapp: QApplication,
) -> None:
    """Leave variant selection empty when no variant is populated."""
    editor = VariantEditorWidget(VariantItem())

    widget = _get_variant_widget(editor)

    assert widget.active_index is None
    assert widget.active_payload is None


def test_variant_field_infers_first_variant(qapp: QApplication) -> None:
    """Infer the first variant from populated model fields."""
    editor = VariantEditorWidget(VariantItem(text="hello"))

    widget = _get_variant_widget(editor)

    assert widget.active_index == 0


def test_variant_field_infers_second_variant(qapp: QApplication) -> None:
    """Infer the second variant from populated model fields."""
    editor = VariantEditorWidget(VariantItem(number=42))

    widget = _get_variant_widget(editor)

    assert widget.active_index == 1


def test_variant_field_rejects_multiple_populated_variants(qapp: QApplication) -> None:
    """Reject models where multiple variants are populated."""
    with pytest.raises(ValueError, match="Multiple variants have populated fields."):
        VariantEditorWidget(VariantItem(text="hello", number=42))


def test_variant_field_creates_all_variant_pages(qapp: QApplication) -> None:
    """Create field widgets for every variant page."""
    editor = MultiFieldVariantEditorWidget(VariantItem(text="hello"))

    widget = _get_variant_widget(editor)

    text_variant, text_widgets = widget.payloads[0]
    number_variant, number_widgets = widget.payloads[1]

    assert isinstance(text_variant, EditorVariant)
    assert text_variant.label == "Text"
    assert set(text_widgets) == {"text", "description"}

    assert isinstance(number_variant, EditorVariant)
    assert number_variant.label == "Number"
    assert set(number_widgets) == {"number"}


def test_variant_field_can_change_active_variant(qapp: QApplication) -> None:
    """Change the active variant programmatically."""
    editor = VariantEditorWidget(VariantItem(text="hello"))

    widget = _get_variant_widget(editor)

    assert widget.active_index == 0

    widget.set_active_variant(1)

    assert widget.active_index == 1


def test_variant_field_changes_variant_from_radio_button(qapp: QApplication) -> None:
    """Change the active variant through user selection."""
    editor = VariantEditorWidget(VariantItem(text="hello"))

    widget = _get_variant_widget(editor)

    buttons = widget.findChildren(QRadioButton)

    assert len(buttons) == 2
    assert buttons[0].isChecked()

    buttons[1].click()

    assert widget.active_index == 1


def test_variant_field_emits_variant_changed_on_user_selection(qapp: QApplication) -> None:
    """Emit variant_changed when the user selects another variant."""
    editor = VariantEditorWidget(VariantItem(text="hello"))

    widget = _get_variant_widget(editor)

    buttons = widget.findChildren(QRadioButton)

    emissions: list[int] = []
    widget.variant_changed.connect(emissions.append)

    buttons[1].click()

    assert emissions == [1]


def test_variant_field_read_only_disables_variant_selection(qapp: QApplication) -> None:
    """Disable variant selection when the variant field is read-only."""
    editor = ReadOnlyVariantEditorWidget(VariantItem(text="hello"))

    widget = _get_variant_widget(editor)

    buttons = widget.findChildren(QRadioButton)

    assert len(buttons) == 2
    assert all(not button.isEnabled() for button in buttons)


def test_variant_field_read_only_disables_variant_page(qapp: QApplication) -> None:
    """Disable the active variant page when the variant field is read-only."""
    editor = ReadOnlyVariantEditorWidget(VariantItem(text="hello"))

    widget = _get_variant_widget(editor)

    assert widget.active_payload is not None

    _, variant_widgets = widget.active_payload

    text_widget = variant_widgets["text"]

    assert not text_widget.isEnabled()


def test_read_only_field_inside_variant_uses_label(qapp: QApplication) -> None:
    """Use a read-only widget for fields marked read-only inside variants."""
    editor = ReadOnlyVariantFieldEditorWidget(VariantItem(text="hello"))

    widget = _get_variant_widget(editor)

    assert widget.active_payload is not None

    _, variant_widgets = widget.active_payload

    assert isinstance(variant_widgets["text"], QLabel)
    assert variant_widgets["text"].text() == "hello"


def test_save_updates_active_variant(qapp: QApplication) -> None:
    """Save values from the active variant."""
    item = VariantItem(text="original")

    editor = VariantEditorWidget(item)

    widget = _get_variant_widget(editor)

    assert widget.active_payload is not None

    _, variant_widgets = widget.active_payload

    text_widget = variant_widgets["text"]

    assert isinstance(text_widget, QLineEdit)

    text_widget.setText("updated")

    editor.save()

    assert item.text == "updated"
    assert item.number is None


def test_save_updates_only_active_variant(qapp: QApplication) -> None:
    """Save fields belonging only to the currently active variant."""
    item = VariantItem(number=10)

    editor = VariantEditorWidget(item)

    widget = _get_variant_widget(editor)
    widget.set_active_variant(0)

    assert widget.active_payload is not None

    _, variant_widgets = widget.active_payload

    text_widget = variant_widgets["text"]

    assert isinstance(text_widget, QLineEdit)

    text_widget.setText("new text")

    editor.save()

    assert item.text == "new text"
    assert item.number == 10


def test_save_does_not_clear_inactive_variant_fields(qapp: QApplication) -> None:
    """Leave fields from inactive variants untouched."""
    item = VariantItem(number=10)

    editor = VariantEditorWidget(item)

    widget = _get_variant_widget(editor)
    widget.set_active_variant(0)

    assert widget.active_payload is not None

    _, variant_widgets = widget.active_payload

    text_widget = variant_widgets["text"]

    assert isinstance(text_widget, QLineEdit)

    text_widget.setText("new text")

    editor.save()

    assert item.text == "new text"
    assert item.number == 10


def test_save_does_not_modify_read_only_variant_field(qapp: QApplication) -> None:
    """Do not save read-only fields inside variants."""
    item = VariantItem(text="original")

    editor = ReadOnlyVariantFieldEditorWidget(item)

    widget = _get_variant_widget(editor)

    assert widget.active_payload is not None

    _, variant_widgets = widget.active_payload

    text_widget = variant_widgets["text"]

    assert isinstance(text_widget, QLabel)

    editor.save()

    assert item.text == "original"


def test_variant_field_rejects_empty_variants(qapp: QApplication) -> None:
    """Reject variant fields without configured variants."""

    class Editor(BaseEditorWidget[VariantItem]):
        FIELDS = (EditorVariantField(label="Variant", variants=()),)

    with pytest.raises(ValueError, match="must define at least one variant"):
        Editor(VariantItem())


def test_nested_editor_is_created_inside_variant(qapp: QApplication) -> None:
    """Create nested editors inside variant pages."""
    editor = NestedVariantEditorWidget(VariantItem(text="hello"))

    widget = _get_variant_widget(editor)

    assert widget.active_payload is not None

    _, variant_widgets = widget.active_payload

    assert isinstance(variant_widgets["text"], EmptyEditorWidget)


def test_nested_editor_inside_variant_does_not_have_save_button(qapp: QApplication) -> None:
    """Do not create save buttons for nested variant editors."""
    editor = NestedVariantEditorWidget(VariantItem(text="hello"))

    widget = _get_variant_widget(editor)

    assert widget.active_payload is not None

    _, variant_widgets = widget.active_payload

    nested_editor = variant_widgets["text"]

    assert isinstance(nested_editor, EmptyEditorWidget)
    assert not hasattr(nested_editor, "_save_button")


def test_refresh_recursively_refreshes_all_variant_fields(qapp: QApplication) -> None:
    """Refresh fields contained by every variant."""
    refresh_count = 0

    class RefreshableEditor(BaseEditorWidget[object]):
        """Nested editor used to observe refresh."""

        FIELDS = ()

        def refresh(self) -> None:
            nonlocal refresh_count

            refresh_count += 1

    class Editor(BaseEditorWidget[VariantItem]):
        """Editor containing refreshable variant fields."""

        FIELDS = (
            EditorVariantField(
                label="Variant",
                variants=(
                    EditorVariant(
                        label="First",
                        fields=(
                            EditorField(
                                name="text",
                                label="Text",
                                editor_widget_type=RefreshableEditor,
                            ),
                        ),
                    ),
                    EditorVariant(
                        label="Second",
                        fields=(
                            EditorField(
                                name="number",
                                label="Number",
                                editor_widget_type=RefreshableEditor,
                            ),
                        ),
                    ),
                ),
            ),
        )

    editor = Editor(VariantItem())

    editor.refresh()

    assert refresh_count == 2
