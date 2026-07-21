"""Contract for a pomodoro's TODO list (spec §2.5)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Callable
from typing import Protocol

from pomodoro.models.todo_row_state import TodoRowState
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum
from pomodoro.shared.validation_result import ValidationResult


class ITodoListView(Protocol):
    """View contract for a pomodoro's TODO list (AGENTS.md §13.4, spec §2.5).

    Driven entirely by discrete, parametrized callbacks rather than a
    holistic form, so this contract has no meaningful `snapshot()` to
    offer and omits it.
    """

    @property
    def is_dirty(self) -> bool:
        """True while an inline edit (new line, rename) is in progress."""
        ...

    @property
    def is_busy(self) -> bool:
        """True while a triggered action is in flight."""
        ...

    @property
    def is_loading(self) -> bool:
        """True while the list is loading or building itself."""
        ...

    def set_enabled(self, enabled: bool) -> None:
        """Grey out or re-enable the whole list."""
        ...

    def notify_error(self, rs: ValidationResult) -> None:
        """Surface a failed action to the user."""
        ...

    def clear(self) -> None:
        """Empty the in-memory list content."""
        ...

    def notify_refresh(self, context: tuple[TodoRowState, ...]) -> None:
        """Replace the displayed rows with `context`."""
        ...

    def notify_item_deleted(self, label: str) -> None:
        """Show the 'Ligne supprimée — Annuler' toast for `label` (spec §2.5)."""
        ...

    def bind_add_item_requested(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when a new line is validated (Entrée)."""
        ...

    def bind_item_renamed(self, callback: Callable[[str, str], None]) -> None:
        """Register the callback fired when an item's label is edited inline."""
        ...

    def bind_item_state_changed(self, callback: Callable[[str, TodoStateEnum], None]) -> None:
        """Register the callback fired when an item's state dropdown changes."""
        ...

    def bind_item_duplicate_clicked(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when an item's duplicate icon is clicked."""
        ...

    def bind_item_delete_clicked(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when an item's delete icon is clicked."""
        ...

    def bind_delete_list_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when 'Supprimer la liste' is confirmed."""
        ...

    def bind_undo_delete_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when the delete toast's 'Annuler' is clicked."""
        ...


# EOF
