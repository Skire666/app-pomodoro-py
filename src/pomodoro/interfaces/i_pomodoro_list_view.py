"""Contract for the pomodoro list screen (spec §2.1)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Callable
from typing import Protocol

from pomodoro.models.pomodoro_list_view_state import PomodoroListViewState
from pomodoro.models.pomodoro_row_state import PomodoroRowState
from pomodoro.shared.enums.pomodoro_sort_mode_enum import PomodoroSortModeEnum
from pomodoro.shared.validation_result import ValidationResult


class IPomodoroListView(Protocol):
    """View contract for the left-hand pomodoro list (AGENTS.md §13.4, spec §2.1)."""

    @property
    def is_dirty(self) -> bool:
        """True while the user holds an unsaved, in-progress edit."""
        ...

    @property
    def is_busy(self) -> bool:
        """True while a triggered action (delete, duplicate, ...) is in flight."""
        ...

    @property
    def is_loading(self) -> bool:
        """True while the view is loading or building itself."""
        ...

    def snapshot(self) -> PomodoroListViewState:
        """Return the current search/filter/sort controls."""
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

    def notify_refresh(self, context: tuple[PomodoroRowState, ...]) -> None:
        """Replace the displayed rows with `context`."""
        ...

    def bind_search_changed(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when the search text changes."""
        ...

    def bind_sort_changed(self, callback: Callable[[PomodoroSortModeEnum], None]) -> None:
        """Register the callback fired when the sort selector changes."""
        ...

    def bind_new_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when '+ Nouveau' is clicked."""
        ...

    def bind_item_start_clicked(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when a card's 'Démarrer' action is clicked."""
        ...

    def bind_item_edit_clicked(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when a card's 'Modifier' action is clicked."""
        ...

    def bind_item_duplicate_clicked(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when a card's 'Dupliquer' action is clicked."""
        ...

    def bind_item_delete_clicked(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when a card's 'Supprimer' action is clicked."""
        ...


# EOF
