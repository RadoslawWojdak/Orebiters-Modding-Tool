from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget

CanOperationProvider = Callable[..., bool]
ChoiceProvider = Callable[..., Sequence[object]]
ChoiceFormatter = Callable[[object], str]
ItemFactory = Callable[..., object]
ValueProvider = Callable[..., object]
VariantSelector = Callable[..., int]


@dataclass(frozen=True, slots=True, kw_only=True)
class EditorField:
    """Configuration for a single editor field."""

    # Model attribute edited by this field.
    name: str

    # Field label, also used as a radio button label inside a variant field.
    label: str

    # Expected value type, used to determine the appropriate editor widget.
    value_type: object | None = None

    # Custom widget used to edit the field's value.
    editor_widget_type: type[BaseEditorWidget[object]] | None = None

    # Whether the field is displayed as read-only.
    read_only: bool = False

    # Factory used to create new items when adding to a list.
    item_factory: ItemFactory | None = None

    # Provides whether new list item can be added.
    can_add_provider: CanOperationProvider | None = None

    # Provides whether list item can be removed.
    can_remove_provider: CanOperationProvider | None = None

    # Provides the value displayed by the field instead of reading it directly from the model.
    value_provider: ValueProvider | None = None

    # Provides the available options for a choice-based field.
    choices_provider: ChoiceProvider | None = None

    # Converts choice values into human-readable labels.
    choice_formatter: ChoiceFormatter = str


@dataclass(frozen=True, slots=True, kw_only=True)
class EditorVariant:
    """Configuration for one alternative representation of a field."""

    # Label displayed next to the variant's radio button.
    label: str

    # Editor fields that make up this variant.
    fields: tuple[EditorField, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class EditorVariantField:
    """Configuration for a field that offers alternative representations."""

    # Main label displayed above the variant selection.
    label: str

    # Available alternatives, each represented by a radio button.
    # Each variant may contain one or more editor fields.
    variants: tuple[EditorVariant, ...]

    # Whether the entire field is read-only, preventing variant selection and editing.
    read_only: bool = False
