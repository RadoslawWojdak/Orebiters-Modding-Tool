from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Column[T]:
    """Describe a table column."""

    header: str
    tooltip: str
    getter: Callable[[T], object]
    sorter: Callable[[T], object] | None = None
    setter: Callable[[T, object], None] | None = None
    filterable: bool = True
    sortable: bool = True
