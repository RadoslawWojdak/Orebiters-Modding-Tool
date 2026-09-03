from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import Mock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget
from orebiters_modding_tool.app.editors.editor_field import EditorField
from orebiters_modding_tool.app.widgets.dictionary_widget import DictionaryWidget
from orebiters_modding_tool.app.widgets.list_widget import ListWidget


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

    # List value used to test ListEditorWidget fields.
    values: list[object] = field(default_factory=list)

    # Dictionary value used to test DictionaryEditorWidget fields.
    mapping: dict[object, object] = field(default_factory=dict)


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


class ValueProviderEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor used for value provider tests."""

    FIELDS = (
        EditorField(
            name="provided_value",
            label="Provided Value",
            value_provider=lambda editor: f"Provided: {editor._item.text}",
        ),
    )


class ChoiceEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor used for choice field tests."""

    FIELDS = (
        EditorField(
            name="text",
            label="Text",
            choices_provider=lambda _editor: ("first", "second", "third"),
            choice_formatter=lambda choice: str(choice).upper(),
        ),
    )


class MissingChoiceProviderEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor used for invalid choice configuration tests."""

    FIELDS = (EditorField(name="text", label="Text"),)


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


class InvalidListEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor containing an invalid list configuration."""

    FIELDS = (EditorField(name="values", label="Values"),)


class DictionaryEditorWidget(BaseEditorWidget[SampleItem]):
    """Editor containing a dictionary field."""

    FIELDS = (
        EditorField(
            name="mapping",
            label="Mapping",
            editor_widget_type=EmptyEditorWidget,
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


class UnsupportedValue:
    """Unsupported value type used for tests."""


@dataclass
class UnsupportedItem:
    """Item containing an unsupported field value."""

    value: UnsupportedValue


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


class TestBaseEditorWidget:
    """Tests for BaseEditorWidget."""

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
        self,
        qapp: object,
        field_name: str,
        widget_type: type[QWidget],
        value: object,
    ) -> None:
        """Create editors for supported basic value types."""
        editor = BasicFieldsEditorWidget(SampleItem())

        field = editor._fields[field_name]

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

    def test_creates_enum_field(self, qapp: object) -> None:
        """Create a combo box for enum values."""
        editor = BasicFieldsEditorWidget(SampleItem())

        field = editor._fields["enum_value"]

        assert isinstance(field, QComboBox)
        assert field.count() == len(SampleEnum)
        assert field.currentData() is SampleEnum.FIRST

        assert field.itemText(0) == "FIRST"
        assert field.itemData(0) is SampleEnum.FIRST

        assert field.itemText(1) == "SECOND"
        assert field.itemData(1) is SampleEnum.SECOND

    def test_creates_empty_field_for_none_value(self, qapp: object) -> None:
        """Create an empty line edit for None."""
        editor = BasicFieldsEditorWidget(SampleItem(optional_value=None))

        field = editor._fields["optional_value"]

        assert isinstance(field, QLineEdit)
        assert field.text() == ""

    def test_uses_value_provider(self, qapp: object) -> None:
        """Use a configured value provider instead of an item attribute."""
        item = SampleItem(text="Custom text")

        editor = ValueProviderEditorWidget(item)

        field = editor._fields["provided_value"]

        assert isinstance(field, QLineEdit)
        assert field.text() == "Provided: Custom text"

    def test_creates_choice_field(self, qapp: object) -> None:
        """Create a combo box from configured choices."""
        editor = ChoiceEditorWidget(SampleItem(text="second"))

        field = editor._fields["text"]

        assert isinstance(field, QComboBox)

        assert field.count() == 3
        assert field.currentData() == "second"
        assert field.currentText() == "SECOND"

        assert field.itemText(0) == "FIRST"
        assert field.itemText(1) == "SECOND"
        assert field.itemText(2) == "THIRD"

    def test_choice_field_raises_without_provider(self, qapp: object) -> None:
        """Raise an error when a choice field has no provider."""
        editor = MissingChoiceProviderEditorWidget(SampleItem())

        field_config = EditorField(name="text", label="Text")

        with pytest.raises(ValueError, match="Choice field 'text' requires a choices provider."):
            editor._create_choice_field(field_config, "Test")

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
    def test_creates_read_only_field(self, qapp: object, value: object, expected_text: str) -> None:
        """Create selectable labels for read-only values."""
        editor = EmptyEditorWidget(object())

        field = editor._create_read_only_field(value)

        assert isinstance(field, QLabel)
        assert field.text() == expected_text

        assert field.textInteractionFlags() & Qt.TextInteractionFlag.TextSelectableByMouse

    def test_field_level_read_only_uses_label(self, qapp: object) -> None:
        """Use a read-only label for a read-only field."""
        editor = ReadOnlyEditorWidget(SampleItem())

        field = editor._fields["text"]

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
    def test_editor_read_only_overrides_all_basic_fields(
        self,
        qapp: object,
        field_name: str,
    ) -> None:
        """Make all basic fields read-only when the editor is read-only."""
        editor = BasicFieldsEditorWidget(SampleItem(), read_only=True)

        field = editor._fields[field_name]

        assert isinstance(field, QLabel)

    def test_creates_custom_editor_widget(self, qapp: object) -> None:
        """Create a configured custom editor widget."""
        editor = CustomEditorWidget(SampleItem())

        field = editor._fields["text"]

        assert isinstance(field, EmptyEditorWidget)

    def test_passes_context_to_custom_editor(self, qapp: object) -> None:
        """Pass shared context to custom editor widgets."""
        context = {"test_key": "test_value"}

        editor = CustomEditorWidget(SampleItem(), context=context)

        field = editor._fields["text"]

        assert isinstance(field, EmptyEditorWidget)
        assert field._context == context

    def test_passes_read_only_to_custom_editor(self, qapp: object) -> None:
        """Pass read-only state to custom editor widgets."""
        editor = CustomEditorWidget(SampleItem(), read_only=True)

        field = editor._fields["text"]

        assert isinstance(field, EmptyEditorWidget)
        assert field._read_only is True

    def test_creates_list_field(self, qapp: object) -> None:
        """Create a ListWidget for list values."""
        values = ["first", "second"]

        editor = ListEditorWidget(SampleItem(values=values))

        field = editor._fields["values"]

        assert isinstance(field, ListWidget)

    def test_list_field_requires_item_factory(self, qapp: object) -> None:
        """Raise an error when a list field has no item factory."""
        with pytest.raises(ValueError, match="List field 'values' requires an item factory."):
            InvalidListEditorWidget(SampleItem())

    def test_list_field_passes_context_to_item_factory(self, qapp: object) -> None:
        """Pass editor context to the list item factory."""
        item_factory = Mock(return_value="new value")

        class ContextListEditorWidget(BaseEditorWidget[SampleItem]):
            """Editor used for list factory context tests."""

            FIELDS = (EditorField(name="values", label="Values", item_factory=item_factory),)

        context = {"test": "value"}

        editor = ContextListEditorWidget(SampleItem(), context=context)

        field = editor._fields["values"]

        assert isinstance(field, ListWidget)

        field._item_factory()

        item_factory.assert_called_once_with(context)

    def test_list_items_use_base_editor_field_logic(self, qapp: object) -> None:
        """Create list item editors using normal field creation logic."""
        editor = ListEditorWidget(SampleItem(values=["first"]))

        field = editor._fields["values"]

        assert isinstance(field, ListWidget)

        item_widget = field._item_widgets[0]

        assert isinstance(item_widget, QLineEdit)
        assert item_widget.text() == "first"

    def test_nested_list_item_raises_error(self, qapp: object) -> None:
        """Reject nested list values."""
        with pytest.raises(ValueError, match="Nested lists are not supported."):
            NestedListEditorWidget(SampleItem(values=[["nested"]]))

    def test_creates_dictionary_field(self, qapp: object) -> None:
        """Create a DictionaryWidget for dictionary values."""
        values = {
            "first": object(),
            "second": object(),
        }

        editor = DictionaryEditorWidget(SampleItem(mapping=values))

        field = editor._fields["mapping"]

        assert isinstance(field, DictionaryWidget)

    def test_dictionary_field_creates_widgets_for_all_items(self, qapp: object) -> None:
        """Create an item widget for every dictionary value."""
        values = {
            "first": object(),
            "second": object(),
        }

        editor = DictionaryEditorWidget(SampleItem(mapping=values))

        field = editor._fields["mapping"]

        assert isinstance(field, DictionaryWidget)
        assert set(field._item_widgets) == {"first", "second"}

        assert isinstance(field._item_widgets["first"], EmptyEditorWidget)
        assert isinstance(field._item_widgets["second"], EmptyEditorWidget)

    def test_dictionary_field_passes_context(self, qapp: object) -> None:
        """Pass shared context to dictionary item editors."""
        context = {"language": "en"}
        values = {"first": object()}

        editor = DictionaryEditorWidget(SampleItem(mapping=values), context=context)

        field = editor._fields["mapping"]

        assert isinstance(field, DictionaryWidget)

        dictionary_editor = field._item_widgets["first"]

        assert isinstance(dictionary_editor, EmptyEditorWidget)
        assert dictionary_editor._context == context

    def test_dictionary_field_passes_read_only_state(self, qapp: object) -> None:
        """Pass read-only state to dictionary item editors."""
        values = {"first": object()}

        editor = DictionaryEditorWidget(SampleItem(mapping=values), read_only=True)

        field = editor._fields["mapping"]

        assert isinstance(field, DictionaryWidget)

        dictionary_editor = field._item_widgets["first"]

        assert isinstance(dictionary_editor, EmptyEditorWidget)
        assert dictionary_editor._read_only is True

    def test_creates_multiple_editor_sections(self, qapp: object) -> None:
        """Split simple and complex fields into separate layout sections."""
        editor = SectionEditorWidget(SampleItem(values=["first"], mapping={"key": object()}))

        layout = editor._layout

        assert isinstance(layout, QVBoxLayout)

        layout_items = [layout.itemAt(index) for index in range(layout.count())]

        form_layouts = [
            item.layout() for item in layout_items if isinstance(item.layout(), QFormLayout)
        ]

        assert len(form_layouts) == 2

    def test_complex_field_label_is_bold(self, qapp: object) -> None:
        """Display complex field labels using bold text."""
        editor = SectionEditorWidget(SampleItem())

        labels = [
            editor._layout.itemAt(index).widget()
            for index in range(editor._layout.count())
            if isinstance(editor._layout.itemAt(index).widget(), QLabel)
        ]

        assert any(
            label.text() == "Values" and label.font().bold()
            for label in labels
            if isinstance(label, QLabel)
        )

        assert any(
            label.text() == "Mapping" and label.font().bold()
            for label in labels
            if isinstance(label, QLabel)
        )

    def test_adds_spacing_between_editor_sections(self, qapp: object) -> None:
        """Add spacing between simple and complex editor sections."""
        editor = SectionEditorWidget(SampleItem())

        spacings = [
            editor._layout.itemAt(index)
            for index in range(editor._layout.count())
            if editor._layout.itemAt(index).spacerItem() is not None
        ]

        assert len(spacings) >= 3

    def test_unsupported_value_raises_error(self, qapp: object) -> None:
        """Raise an error for unsupported field values."""
        with pytest.raises(ValueError, match="Unsupported field type: UnsupportedValue."):
            UnsupportedEditorWidget(UnsupportedItem(value=UnsupportedValue()))

    def test_default_context_is_empty_dictionary(self, qapp: object) -> None:
        """Use an empty dictionary when no context is provided."""
        editor = BasicFieldsEditorWidget(SampleItem())

        assert editor._context == {}

    def test_preserves_provided_context(self, qapp: object) -> None:
        """Use the provided context dictionary."""
        context = {"key": "value"}

        editor = BasicFieldsEditorWidget(SampleItem(), context=context)

        assert editor._context is context
