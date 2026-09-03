from enum import Enum

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

from orebiters_modding_tool.app.editors.editor_field import EditorField
from orebiters_modding_tool.app.widgets.dictionary_widget import DictionaryWidget
from orebiters_modding_tool.app.widgets.list_widget import ListWidget


class BaseEditorWidget[T](QWidget):
    """Base widget for editing object properties."""

    SECTION_SPACING = 12

    FIELDS: tuple[EditorField, ...] = ()

    def __init__(
        self,
        item: T,
        context: dict[str, object] | None = None,
        parent: QWidget | None = None,
        *,
        read_only: bool = False,
    ) -> None:
        """Initialize the editor.

        :param item: Item being edited.
        :param context: Additional data required by editor fields.
        :param parent: Optional parent widget.
        :param read_only: Whether the entire editor is read-only.
        """
        super().__init__(parent)

        self._item = item
        self._context = {} if context is None else context
        self._read_only = read_only

        self._setup_fields()

    def _setup_fields(self) -> None:
        """Create and add editor fields."""
        self._fields: dict[str, QWidget] = {}
        self._layout = QVBoxLayout(self)

        form_layout: QFormLayout | None = None

        for field_config in self.FIELDS:
            value = self._get_field_value(field_config)
            field = self._create_field(field_config, value)

            self._fields[field_config.name] = field

            if self._is_complex_field(field_config, value):
                form_layout = None

                self._add_section_spacing()
                self._add_complex_field(field_config, field)
                continue

            if form_layout is None:
                self._add_section_spacing()

                form_layout = QFormLayout()
                self._layout.addLayout(form_layout)

            form_layout.addRow(field_config.label, field)

        self._layout.addStretch()

    def _get_field_value(self, field_config: EditorField) -> object:
        """Get the value displayed by an editor field.

        :param field_config: Field configuration.
        :returns: Field value.
        """
        if field_config.value_provider is not None:
            return field_config.value_provider(self)

        return getattr(self._item, field_config.name)

    @staticmethod
    def _is_complex_field(field_config: EditorField, value: object) -> bool:
        """Check whether a field requires full-width layout.

        :param field_config: Field configuration.
        :param value: Field value.
        :returns: True if the field requires a full-width layout.
        """
        return isinstance(value, (list, dict)) or field_config.editor_widget_type is not None

    def _add_complex_field(self, field_config: EditorField, field: QWidget) -> None:
        """Add a full-width editor field.

        :param field_config: Field configuration.
        :param field: Editor widget.
        """
        label = QLabel(field_config.label, self)

        font = label.font()
        font.setBold(True)

        label.setFont(font)

        self._layout.addWidget(label)
        self._layout.addWidget(field)

    def _add_section_spacing(self) -> None:
        """Add spacing before a new editor section."""
        if self._layout.count() > 0:
            self._layout.addSpacing(self.SECTION_SPACING)

    def _create_field(self, field_config: EditorField, value: object) -> QWidget:
        """Create an editor widget for a field value.

        :param field_config: Configuration of the field.
        :param value: Current field value.
        :returns: Configured editor widget.
        :raises ValueError: If the field type is unsupported.
        """
        read_only = self._read_only or field_config.read_only

        if isinstance(value, list):
            return self._create_list_field(field_config, value)

        if isinstance(value, dict):
            return self._create_dict_field(field_config, value)

        if field_config.editor_widget_type is not None:
            return field_config.editor_widget_type(value, self._context, self, read_only=read_only)

        if read_only:
            return self._create_read_only_field(value)

        if field_config.choices_provider is not None:
            return self._create_choice_field(field_config, value)

        if isinstance(value, str):
            return self._create_str_field(value)

        if isinstance(value, bool):
            return self._create_bool_field(value)

        if isinstance(value, int):
            return self._create_int_field(value)

        if isinstance(value, float):
            return self._create_float_field(value)

        if isinstance(value, Enum):
            return self._create_enum_field(value)

        if value is None:
            return self._create_none_field()

        raise ValueError(f"Unsupported field type: {type(value).__name__}.")

    def _create_read_only_field(self, value: object) -> QLabel:
        """Create a selectable read-only field display.

        :param value: Value to display.
        :returns: Read-only value display.
        """
        text = "-" if value is None else str(value)

        field = QLabel(text, self)
        field.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        return field

    def _create_choice_field(self, field_config: EditorField, value: object) -> QComboBox:
        """Create an editor for a predefined set of choices.

        :param field_config: Configuration of the field.
        :param value: Currently selected value.
        :returns: Configured choice editor.
        """
        if field_config.choices_provider is None:
            raise ValueError(f"Choice field '{field_config.name}' requires a choices provider.")

        choices = field_config.choices_provider(self)

        field = QComboBox(self)

        for choice in choices:
            field.addItem(field_config.choice_formatter(choice), choice)

        current_index = field.findData(value)

        if current_index >= 0:
            field.setCurrentIndex(current_index)

        return field

    def _create_str_field(self, value: str) -> QLineEdit:
        """Create an editor for a string field.

        :param value: Initial field value.
        :returns: Configured text input.
        """
        return QLineEdit(value, self)

    def _create_int_field(self, value: int) -> QSpinBox:
        """Create an editor for an integer field.

        :param value: Initial field value.
        :returns: Configured integer editor.
        """
        field = QSpinBox(self)
        field.setValue(value)

        return field

    def _create_float_field(self, value: float) -> QDoubleSpinBox:
        """Create an editor for a floating-point field.

        :param value: Initial field value.
        :returns: Configured floating-point editor.
        """
        field = QDoubleSpinBox(self)
        field.setValue(value)

        return field

    def _create_bool_field(self, value: bool) -> QCheckBox:
        """Create an editor for a boolean field.

        :param value: Initial field value.
        :returns: Configured boolean editor.
        """
        field = QCheckBox(self)
        field.setChecked(value)

        return field

    def _create_enum_field(self, value: Enum) -> QComboBox:
        """Create an editor for an enum field.

        :param value: Initial enum value.
        :returns: Configured enum editor.
        """
        enum_type = type(value)
        field = QComboBox(self)

        for enum_value in enum_type:
            field.addItem(enum_value.name, enum_value)

        current_index = field.findData(value)

        if current_index >= 0:
            field.setCurrentIndex(current_index)

        return field

    def _create_none_field(self) -> QLineEdit:
        """Create an editor for an empty value.

        :returns: Configured empty text input.
        """
        return QLineEdit(self)

    def _create_list_field(
        self,
        field_config: EditorField,
        values: list[object],
    ) -> ListWidget:
        """Create an editor for a list field.

        :param field_config: Configuration of the field.
        :param values: Initial list values.
        :returns: Configured list editor.
        :raises ValueError: If no item factory is configured.
        """
        item_factory = field_config.item_factory

        if item_factory is None:
            raise ValueError(f"List field '{field_config.name}' requires an item factory.")

        read_only = self._read_only or field_config.read_only

        return ListWidget(
            item_factory=lambda: item_factory(self._context),
            item_widget_factory=lambda value: self._create_list_item_field(field_config, value),
            values=values,
            parent=self,
            can_add=not read_only,
            can_remove=not read_only,
        )

    def _create_list_item_field(self, field_config: EditorField, value: object) -> QWidget:
        """Create an editor widget for a list item.

        :param field_config: Configuration of the parent list field.
        :param value: List item value.
        :returns: Configured list item editor.
        :raises ValueError: If the list item type is unsupported.
        """
        if isinstance(value, list):
            raise ValueError("Nested lists are not supported.")

        return self._create_field(field_config, value)

    def _create_dict_field(
        self,
        field_config: EditorField,
        items: dict[object, object],
    ) -> DictionaryWidget:
        """Create an editor for a dictionary field.

        :param field_config: Configuration of the field.
        :param items: Initial dictionary items.
        :returns: Configured dictionary widget.
        """
        return DictionaryWidget(
            item_widget_factory=lambda value: self._create_dict_item_field(field_config, value),
            items=items,
            parent=self,
        )

    def _create_dict_item_field(self, field_config: EditorField, value: object) -> QWidget:
        """Create an editor widget for a dictionary value.

        :param field_config: Configuration of the parent dictionary field.
        :param value: Dictionary value.
        :returns: Configured dictionary value widget.
        :raises ValueError: If the dictionary value type is unsupported.
        """
        if isinstance(value, dict):
            raise ValueError("Nested dictionaries are not supported.")

        return self._create_field(field_config, value)
