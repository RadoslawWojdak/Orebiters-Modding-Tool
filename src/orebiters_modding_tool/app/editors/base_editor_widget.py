from collections.abc import Callable, Sequence
from dataclasses import replace
from enum import Enum
from types import UnionType
from typing import Union, get_args, get_origin, get_type_hints

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from orebiters_modding_tool.app.editors.editor_field import (
    EditorField,
    EditorVariant,
    EditorVariantField,
)
from orebiters_modding_tool.app.widgets.dictionary_widget import DictionaryWidget
from orebiters_modding_tool.app.widgets.dynamic_combo_box import DynamicComboBox
from orebiters_modding_tool.app.widgets.list_widget import ListWidget
from orebiters_modding_tool.app.widgets.variant_widget import VariantWidget

VariantPayload = tuple[EditorVariant, dict[str, QWidget]]


class BaseEditorWidget[T](QWidget):
    """Base widget for editing object properties."""

    SECTION_SPACING = 12
    NUMBER_MIN = -1_000_000_000
    NUMBER_MAX = 1_000_000_000

    FIELDS: tuple[EditorField | EditorVariantField, ...] = ()

    saved = Signal()

    def __init__(
        self,
        item: T,
        context: dict[str, object] | None = None,
        parent: QWidget | None = None,
        *,
        read_only: bool = False,
        show_save_button: bool = True,
    ) -> None:
        """Initialize the editor.

        :param item: Item being edited.
        :param context: Additional data required by editor fields.
        :param parent: Optional parent widget.
        :param read_only: Whether the editor is read-only.
        :param show_save_button: Whether to display the save button.
        """
        super().__init__(parent)

        self._item = item
        self._context = {} if context is None else context
        self._read_only = read_only
        self._show_save_button = show_save_button

        self._widgets: list[QWidget] = []

        self._layout = QVBoxLayout(self)

        self._setup_fields()

    # =========================================================================
    # Public API
    # =========================================================================

    @property
    def item(self) -> T:
        """Return the edited item."""
        return self._item

    def save(self) -> None:
        """Save the current editor state to the edited item."""
        values: dict[str, object] = {}

        for field_config, widget in zip(self.FIELDS, self._widgets, strict=True):
            if isinstance(field_config, EditorVariantField):
                self._collect_variant_values(widget, values)
                continue

            self._collect_field_value(field_config, widget, values)

        for name, value in values.items():
            setattr(self._item, name, value)

        self.saved.emit()

    def refresh(self) -> None:
        """Refresh this editor and its nested editors."""
        for widget in self._widgets:
            self._refresh_field(widget)

    # =========================================================================
    # Setup
    # =========================================================================

    def _setup_fields(self) -> None:
        """Create the editor layout."""
        ordinary_fields: list[EditorField] = []

        for field_config in self.FIELDS:
            if isinstance(field_config, EditorVariantField):
                self._add_field_group(ordinary_fields)
                ordinary_fields.clear()

                self._add_variant_field(field_config)
                continue

            value = self._get_field_value(field_config)

            if self._is_complex_field(field_config, value):
                self._add_field_group(ordinary_fields)
                ordinary_fields.clear()

                self._add_complex_field(field_config, value)
                continue

            ordinary_fields.append(field_config)

        self._add_field_group(ordinary_fields)

        self._layout.addStretch()
        self._setup_save_button()

    def _add_field_group(self, fields: Sequence[EditorField]) -> None:
        """Add a group of ordinary editor fields."""
        if not fields:
            return

        self._add_section_spacing()

        form_layout = QFormLayout()
        self._layout.addLayout(form_layout)

        for field_config in fields:
            value = self._get_field_value(field_config)
            widget = self._create_field(field_config, value)

            self._widgets.append(widget)

            form_layout.addRow(field_config.label, widget)

    def _add_complex_field(self, field_config: EditorField, value: object) -> None:
        """Create and add a full-width editor field.

        :param field_config: Field configuration.
        :param value: Current field value.
        """
        self._add_section_spacing()

        widget = self._create_field(field_config, value)
        self._widgets.append(widget)

        self._add_complex_widget(field_config, widget, self._layout, self)

    def _add_variant_field(self, field_config: EditorVariantField) -> None:
        """Add a variant editor to the layout."""
        self._add_section_spacing()

        self._layout.addWidget(self._create_section_label(field_config.label, self))

        widget = self._create_variant_field(field_config)

        self._widgets.append(widget)
        self._layout.addWidget(widget)

    def _setup_save_button(self) -> None:
        """Create the save button when enabled."""
        if self._read_only or not self._show_save_button:
            return

        self._save_button = QPushButton("Save", self)
        self._save_button.clicked.connect(self.save)

        self._layout.addWidget(self._save_button)

    # =========================================================================
    # Variant handling
    # =========================================================================

    def _create_variant_field(
        self,
        field_config: EditorVariantField,
    ) -> VariantWidget[VariantPayload]:
        """Create a variant widget.

        :param field_config: Variant field configuration.
        :returns: Configured variant widget.
        :raises ValueError: If no variants are defined.
        """
        if not field_config.variants:
            raise ValueError(
                f"Variant field '{field_config.label}' must define at least one variant."
            )

        initial_index = self._get_initial_variant_index(field_config)
        variants: list[tuple[str, QWidget, VariantPayload]] = []

        for variant in field_config.variants:
            page, widgets = self._create_variant_page(field_config, variant)
            variants.append(
                (
                    variant.label,
                    page,
                    (variant, widgets),
                )
            )

        return VariantWidget(
            variants=variants,
            initial_index=initial_index,
            parent=self,
            read_only=self._read_only or field_config.read_only,
        )

    def _create_variant_page(
        self,
        variant_field_config: EditorVariantField,
        variant: EditorVariant,
    ) -> tuple[QWidget, dict[str, QWidget]]:
        """Create the editor page for a variant.

        :param variant_field_config: Variant field configuration.
        :param variant: Variant configuration.
        :returns: Variant page and its field widgets.
        """
        page = QWidget(self)
        layout = QVBoxLayout(page)
        widgets: dict[str, QWidget] = {}

        form_layout: QFormLayout | None = None

        for field_config in variant.fields:
            value = self._get_field_value(field_config)
            widget = self._create_field(field_config, value)

            widgets[field_config.name] = widget

            if self._is_complex_field(field_config, value):
                form_layout = None

                self._add_complex_widget(field_config, widget, layout, page)
                continue

            if form_layout is None:
                form_layout = QFormLayout()
                layout.addLayout(form_layout)

            form_layout.addRow(field_config.label, widget)

        layout.addStretch()

        if self._read_only or variant_field_config.read_only:
            self._set_widget_read_only(page)

        return page, widgets

    def _get_initial_variant_index(self, field_config: EditorVariantField) -> int | None:
        """Determine the initially selected variant."""
        return self._infer_variant_index(field_config)

    @staticmethod
    def _validate_variant_index(field_config: EditorVariantField, index: int) -> None:
        """Validate a variant index.

        :param field_config: Variant field configuration.
        :param index: Variant index to validate.
        :raises ValueError: If the index is invalid.
        """
        if type(index) is not int or not 0 <= index < len(field_config.variants):
            raise ValueError(f"Invalid variant index {index!r} for '{field_config.label}'.")

    def _infer_variant_index(self, field_config: EditorVariantField) -> int | None:
        """Determine the variant from populated model fields.

        :param field_config: Variant field configuration.
        :returns: Populated variant index, or None if none are populated.
        :raises ValueError: If multiple variants are populated.
        """
        populated_variants = [
            index
            for index, variant in enumerate(field_config.variants)
            if any(getattr(self._item, field.name, None) is not None for field in variant.fields)
        ]

        if not populated_variants:
            return None

        if len(populated_variants) == 1:
            return populated_variants[0]

        raise ValueError(
            f"Cannot infer the active variant for '{field_config.label}'. "
            "Multiple variants have populated fields."
        )

    # =========================================================================
    # Field lookup
    # =========================================================================

    def _get_field_widget(self, name: str) -> QWidget | None:
        """Get a field widget by its name.

        :param name: Field name.
        :returns: Field widget, or None if it has not been created.
        """
        for field_config, widget in zip(self.FIELDS, self._widgets, strict=False):
            if isinstance(field_config, EditorField) and field_config.name == name:
                return widget

        return None

    # =========================================================================
    # Field values
    # =========================================================================

    def _get_field_value(self, field_config: EditorField) -> object:
        """Get the value displayed by a field.

        :param field_config: Field configuration.
        :returns: Value displayed by the field.
        """
        if field_config.value_provider is not None:
            return field_config.value_provider(self)

        return getattr(self._item, field_config.name)

    def _collect_field_value(
        self,
        field_config: EditorField,
        widget: QWidget,
        values: dict[str, object],
    ) -> None:
        """Collect an editable field value.

        :param field_config: Field configuration.
        :param widget: Field widget.
        :param values: Dictionary receiving collected values.
        """
        if field_config.read_only:
            return

        if field_config.value_provider is not None:
            return

        values[field_config.name] = self._get_field_value_for_save(widget, field_config.value_type)

    def _collect_variant_values(self, widget: QWidget, values: dict[str, object]) -> None:
        """Collect values from the active variant.

        :param widget: Variant widget.
        :param values: Dictionary receiving collected values.
        :raises TypeError: If the widget is not a VariantWidget.
        """
        if not isinstance(widget, VariantWidget):
            raise TypeError(f"Expected VariantWidget, got {type(widget).__name__}.")

        payload = widget.active_payload
        if payload is None:
            return

        variant, variant_widgets = payload

        for field_config in variant.fields:
            self._collect_field_value(field_config, variant_widgets[field_config.name], values)

    # =========================================================================
    # Field creation
    # =========================================================================

    def _create_field(self, field_config: EditorField, value: object) -> QWidget:
        """Create an editor widget for a field.

        :param field_config: Field configuration.
        :param value: Current field value.
        :returns: Created editor widget.
        :raises ValueError: If the field type is unsupported.
        """
        read_only = self._read_only or field_config.read_only

        if isinstance(value, list):
            return self._create_list_field(field_config, value)

        if isinstance(value, dict):
            return self._create_dict_field(field_config, value)

        if field_config.editor_widget_type is not None:
            return field_config.editor_widget_type(
                value,
                self._context,
                self,
                read_only=read_only,
                show_save_button=False,
            )

        if read_only:
            return self._create_read_only_field(value)

        if field_config.choices_provider is not None:
            return self._create_choice_field(field_config, value)

        value_type, allows_none = self._get_effective_type(field_config, value)

        if value_type is str:
            return self._create_str_field(value if isinstance(value, str) else "")

        if value_type is bool:
            return self._create_bool_field(value if isinstance(value, bool) else False)

        if value_type is int:
            if allows_none:
                return self._create_optional_number_field(value, int)

            return self._create_int_field(value if isinstance(value, int) else 0)

        if value_type is float:
            if allows_none:
                return self._create_optional_number_field(value, float)

            return self._create_float_field(value if isinstance(value, (int, float)) else 0.0)

        if isinstance(value, Enum):
            return self._create_enum_field(value)

        if value_type is not None and issubclass(value_type, Enum):
            return self._create_enum_type_field(value_type, value)

        if value is None:
            return self._create_none_field()

        raise ValueError(f"Unsupported field type: {type(value).__name__}.")

    def _create_read_only_field(self, value: object) -> QLabel:
        """Create a read-only field display."""
        field = QLabel("-" if value is None else str(value), self)
        field.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        return field

    def _create_choice_field(
        self,
        field_config: EditorField,
        value: object,
    ) -> DynamicComboBox[object]:
        """Create an editor for a predefined set of choices.

        :param field_config: Field configuration.
        :param value: Current field value.
        :returns: Choice editor widget.
        :raises ValueError: If no choices provider is configured.
        """
        provider = field_config.choices_provider

        if provider is None:
            raise ValueError(f"Choice field '{field_config.name}' requires a choices provider.")

        field = DynamicComboBox(
            choices_provider=lambda current_value: provider(self, current_value),
            choice_formatter=field_config.choice_formatter,
            parent=self,
        )

        field.setCurrentIndex(field.find_data_equal(value))

        return field

    def _create_str_field(self, value: str) -> QLineEdit:
        """Create an editor for a string field.

        :param value: Current field value.
        :returns: Text editor widget.
        """
        return QLineEdit(value, self)

    def _create_int_field(self, value: int) -> QSpinBox:
        """Create an editor for an integer field.

        :param value: Current field value.
        :returns: Integer editor widget.
        """
        field = QSpinBox(self)
        field.setRange(self.NUMBER_MIN, self.NUMBER_MAX)
        field.setValue(value)

        return field

    def _create_float_field(self, value: float) -> QDoubleSpinBox:
        """Create an editor for a floating-point field.

        :param value: Current field value.
        :returns: Floating-point editor widget.
        """
        field = QDoubleSpinBox(self)
        field.setRange(float(self.NUMBER_MIN), float(self.NUMBER_MAX))
        field.setValue(value)

        return field

    def _create_optional_number_field(
        self,
        value: object,
        value_type: type[int] | type[float],
    ) -> QLineEdit:
        """Create an editor for an optional numeric value.

        :param value: Current field value.
        :returns: Text editor widget.
        """
        field = QLineEdit("" if value is None else str(value), self)

        field.setPlaceholderText("Integer or empty" if value_type is int else "Number or empty")

        return field

    def _create_bool_field(self, value: bool) -> QCheckBox:
        """Create an editor for a boolean field.

        :param value: Current field value.
        :returns: Boolean editor widget.
        """
        field = QCheckBox(self)
        field.setChecked(value)

        return field

    def _create_enum_field(self, value: Enum) -> QComboBox:
        """Create an editor for an enum value.

        :param value: Current field value.
        :returns: Enum editor widget.
        """
        return self._create_enum_type_field(type(value), value)

    def _create_enum_type_field(self, enum_type: type[Enum], value: object) -> QComboBox:
        """Create an editor for an enum type.

        :param enum_type: Enum type.
        :param value: Current field value.
        :returns: Enum editor widget.
        """
        field = QComboBox(self)

        for enum_value in enum_type:
            field.addItem(enum_value.name, enum_value)

        current_index = field.findData(value)

        if current_index >= 0:
            field.setCurrentIndex(current_index)

        return field

    def _create_none_field(self) -> QLineEdit:
        """Create an editor for an untyped empty value.

        :returns: Empty text editor widget.
        """
        return QLineEdit(self)

    # =========================================================================
    # Collection fields
    # =========================================================================

    def _create_list_field(
        self,
        field_config: EditorField,
        values: list[object],
    ) -> ListWidget:
        """Create an editor for a list field.

        :param field_config: Field configuration.
        :param values: Current list values.
        :returns: List editor widget.
        :raises ValueError: If no item factory is configured.
        """
        read_only = self._read_only or field_config.read_only

        return ListWidget(
            item_factory=lambda: self._create_default_list_item(field_config),
            item_widget_factory=lambda value: self._create_list_item_field(field_config, value),
            values=values,
            parent=self,
            can_add_provider=self._get_operation_provider(
                field_config.can_add_provider,
                read_only,
            ),
            can_remove_provider=self._get_operation_provider(
                field_config.can_remove_provider,
                read_only,
            ),
        )

    def _create_list_item_field(self, field_config: EditorField, value: object) -> QWidget:
        """Create an editor widget for a list item.

        :param field_config: List field configuration.
        :param value: Current item value.
        :returns: Item editor widget.
        :raises ValueError: If nested lists are used or the item type cannot be determined.
        """
        if isinstance(value, list):
            raise ValueError("Nested lists are not supported.")

        item_type = self._get_list_item_type(field_config.value_type)

        if item_type is None:
            if value is None:
                raise ValueError("Cannot infer list item type from None value.")

            item_type = type(value)

        item_config = replace(field_config, value_type=item_type)

        return self._create_field(item_config, value)

    def _create_default_list_item(self, field_config: EditorField) -> object:
        """Create a default value for a new list item.

        :param field_config: List field configuration.
        :returns: Default list item.
        :raises ValueError: If the item type cannot be determined.
        """
        if field_config.item_factory is not None:
            return field_config.item_factory(self._context)

        field_type = self._get_field_annotation(field_config.name)

        item_type = self._get_list_item_type(field_type)

        if item_type is None:
            raise ValueError(f"Cannot determine item type for list field '{field_config.name}'.")

        defaults = {
            str: "",
            int: 0,
            float: 0.0,
            bool: False,
        }

        if item_type in defaults:
            return defaults[item_type]

        if isinstance(item_type, type) and issubclass(item_type, Enum):
            try:
                return next(iter(item_type))
            except StopIteration as error:
                raise ValueError(
                    f"Enum for list field '{field_config.name}' has no values."
                ) from error

        raise ValueError(
            f"List field '{field_config.name}' requires an item factory "
            f"for type '{self._type_name(item_type)}'."
        )

    def _create_dict_field(
        self,
        field_config: EditorField,
        items: dict[object, object],
    ) -> DictionaryWidget:
        """Create an editor for a dictionary field.

        :param field_config: Field configuration.
        :param items: Current dictionary values.
        :returns: Dictionary editor widget.
        """
        return DictionaryWidget(
            item_widget_factory=lambda value: self._create_dict_item_field(field_config, value),
            items=items,
            parent=self,
        )

    def _create_dict_item_field(self, field_config: EditorField, value: object) -> QWidget:
        """Create an editor widget for a dictionary value.

        :param field_config: Field configuration.
        :param value: Dictionary value.
        :returns: Value editor widget.
        :raises ValueError: If nested dictionaries are used.
        """
        if isinstance(value, dict):
            raise ValueError("Nested dictionaries are not supported.")

        return self._create_field(field_config, value)

    # =========================================================================
    # Saving
    # =========================================================================

    def _get_field_value_for_save(self, field: QWidget, value_type: object = None) -> object:
        """Get the value represented by an editor widget.

        :param field: Editor widget.
        :param value_type: Expected field type.
        :returns: Value represented by the widget.
        :raises ValueError: If the value cannot be converted.
        """
        if isinstance(field, ListWidget):
            return self._get_list_value_for_save(field)

        if isinstance(field, DictionaryWidget):
            return self._get_dictionary_value_for_save(field)

        if isinstance(field, BaseEditorWidget):
            return self._save_nested_editor(field)

        value = self._get_base_widget_value(field)

        if value_type is None:
            return value

        expected_type, allows_none = self._get_type_info(value_type)

        if isinstance(field, QLineEdit) and expected_type in (int, float):
            text = field.text().strip()

            if not text:
                if allows_none:
                    return None

                raise ValueError("This field cannot be empty.")

            try:
                return expected_type(text)
            except ValueError as error:
                raise ValueError(f"Invalid {expected_type.__name__} value: {text!r}.") from error

        return value

    @staticmethod
    def _save_nested_editor(editor: BaseEditorWidget[object]) -> object:
        """Save a nested editor and return its edited item.

        :param editor: Nested editor widget to save.
        :returns: Item edited by the nested editor.
        """
        editor.save()
        return editor.item

    def _get_list_value_for_save(self, widget: ListWidget) -> list[object]:
        """Get values from a list widget for saving.

        Nested editor widgets are saved while their values are collected.

        :param widget: List widget containing item editor widgets.
        :returns: Current list values.
        """
        return [self._get_field_value_for_save(item_widget) for item_widget in widget._item_widgets]

    def _get_dictionary_value_for_save(self, widget: DictionaryWidget) -> dict[object, object]:
        """Get values from a dictionary widget for saving.

        Nested editor widgets are saved while their values are collected.

        :param widget: Dictionary widget containing item editor widgets.
        :returns: Current dictionary values.
        """
        return {
            key: self._get_field_value_for_save(item_widget)
            for key, item_widget in widget._item_widgets.items()
        }

    @staticmethod
    def _get_base_widget_value(field: QWidget) -> object:
        """Get the current value from a basic editor widget.

        :param field: Basic editor widget.
        :returns: Current widget value.
        :raises ValueError: If the widget type is unsupported.
        """
        if isinstance(field, QLineEdit):
            return field.text()

        if isinstance(field, QSpinBox):
            return field.value()

        if isinstance(field, QDoubleSpinBox):
            return field.value()

        if isinstance(field, QCheckBox):
            return field.isChecked()

        if isinstance(field, QComboBox):
            return field.currentData()

        raise ValueError(f"Unsupported editor widget type: {type(field).__name__}.")

    # =========================================================================
    # Type helpers
    # =========================================================================

    @staticmethod
    def _get_type_info(value_type: object) -> tuple[type | None, bool]:
        """Get the underlying type and whether None is allowed.

        :param value_type: Type annotation.
        :returns: Underlying type and optionality.
        """
        origin = get_origin(value_type)

        if origin not in (Union, UnionType):
            if isinstance(value_type, type):
                return value_type, False

            return None, False

        args = get_args(value_type)
        allows_none = type(None) in args
        non_none_args = tuple(arg for arg in args if arg is not type(None))

        if len(non_none_args) == 1 and isinstance(non_none_args[0], type):
            return non_none_args[0], allows_none

        return None, allows_none

    @classmethod
    def _get_effective_type(
        cls,
        field_config: EditorField,
        value: object,
    ) -> tuple[type | None, bool]:
        """Determine the effective field type.

        :param field_config: Field configuration.
        :param value: Current field value.
        :returns: Effective type and optionality.
        """
        if field_config.value_type is not None:
            return cls._get_type_info(field_config.value_type)

        if value is None:
            return None, False

        return type(value), False

    @staticmethod
    def _get_list_item_type(value_type: object) -> object | None:
        """Get the item type declared by a list annotation.

        :param value_type: List type annotation.
        :returns: Declared item type, or None.
        """
        if get_origin(value_type) is not list:
            return None

        args = get_args(value_type)

        return args[0] if args else None

    def _get_field_annotation(self, field_name: str) -> object:
        """Get a model field annotation.

        :param field_name: Model field name.
        :returns: Field annotation.
        :raises ValueError: If the annotation cannot be determined.
        """
        try:
            return get_type_hints(type(self._item))[field_name]
        except (KeyError, NameError, TypeError) as error:
            raise ValueError(f"Cannot determine type for field '{field_name}'.") from error

    # =========================================================================
    # Layout helpers
    # =========================================================================

    def _add_complex_widget(
        self,
        field_config: EditorField,
        field: QWidget,
        layout: QVBoxLayout,
        parent: QWidget,
    ) -> None:
        """Add a full-width editor field.

        :param field_config: Field configuration.
        :param field: Editor widget.
        :param layout: Target layout.
        :param parent: Widget used as the label parent.
        """
        layout.addWidget(self._create_section_label(field_config.label, parent))
        layout.addWidget(field)

    @staticmethod
    def _create_section_label(text: str, parent: QWidget) -> QLabel:
        """Create a bold section label.

        :param text: Label text.
        :param parent: Label parent.
        :returns: Configured label.
        """
        label = QLabel(text, parent)

        font = label.font()
        font.setBold(True)
        label.setFont(font)

        return label

    def _add_section_spacing(self) -> None:
        """Add spacing before a new editor section."""
        if self._layout.count() > 0:
            self._layout.addSpacing(self.SECTION_SPACING)

    @staticmethod
    def _set_widget_read_only(widget: QWidget) -> None:
        """Disable editing for a widget."""
        widget.setEnabled(False)

    @staticmethod
    def _is_complex_field(field_config: EditorField, value: object) -> bool:
        """Determine whether a field requires a full-width layout.

        :param field_config: Field configuration.
        :param value: Current field value.
        :returns: Whether the field is complex.
        """
        return isinstance(value, (list, dict)) or field_config.editor_widget_type is not None

    # =========================================================================
    # Miscellaneous Helpers
    # =========================================================================

    def _get_operation_provider(
        self,
        provider: Callable[..., bool] | None,
        read_only: bool,
    ) -> Callable[[], bool] | None:
        """Create a bound operation provider.

        :param provider: Operation provider.
        :param read_only: Whether the editor is read-only.
        :returns: Bound provider, or None.
        """
        if read_only:
            return lambda: False

        if provider is None:
            return None

        return lambda: provider(self)

    def _refresh_field(self, field: QWidget) -> None:
        """Refresh a field and its nested editors."""
        if isinstance(field, BaseEditorWidget):
            field.refresh()
            return

        if isinstance(field, ListWidget):
            field.refresh()

            for index in range(field.item_count()):
                self._refresh_field(field.item_at(index))

            return

        if isinstance(field, DictionaryWidget):
            field.refresh()

            for item_widget in field._item_widgets.values():
                self._refresh_field(item_widget)

            return

        if isinstance(field, VariantWidget):
            for payload in field.payloads:
                if payload is None:
                    continue

                _, widgets = payload

                for nested_field in widgets.values():
                    self._refresh_field(nested_field)

    @staticmethod
    def _type_name(value_type: object) -> str:
        """Get a readable type name.

        :param value_type: Type to format.
        :returns: Readable type name.
        """
        return getattr(value_type, "__name__", str(value_type))
