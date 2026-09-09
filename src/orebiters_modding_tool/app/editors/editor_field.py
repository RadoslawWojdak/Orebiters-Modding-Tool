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


@dataclass(frozen=True, slots=True, kw_only=True)
class EditorField:
    """Configuration for an editor field."""

    name: str
    label: str
    read_only: bool = False

    # Factory used to create new list items.
    item_factory: ItemFactory | None = None

    # Provides whether new list items can be added.
    can_add_provider: CanOperationProvider | None = None

    # Provides whether new list items can be removed.
    can_remove_provider: CanOperationProvider | None = None

    # Custom editor used for field values.
    editor_widget_type: type[BaseEditorWidget[object]] | None = None

    # Provides the displayed field value.
    value_provider: ValueProvider | None = None

    # Provides available values for choice fields.
    choices_provider: ChoiceProvider | None = None

    # Converts choice values into display text.
    choice_formatter: ChoiceFormatter = str
