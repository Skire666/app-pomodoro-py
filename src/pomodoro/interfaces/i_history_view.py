"""Contract for the history screen (spec §2.6)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from typing import Protocol

from pomodoro.models.pomodoro_history_row_state import PomodoroHistoryRowState
from pomodoro.models.todo_history_row_state import TodoHistoryRowState
from pomodoro.shared.validation_result import ValidationResult


class IHistoryView(Protocol):
    """View contract for the read-only history screen (AGENTS.md §13.4, spec §2.6).

    Purely a display of two tables with no editable form, so this contract
    has no meaningful `snapshot()` to offer and omits it.
    """

    @property
    def is_busy(self) -> bool:
        """True while a refresh is in flight."""
        ...

    @property
    def is_loading(self) -> bool:
        """True while the screen is loading or building itself."""
        ...

    def set_enabled(self, enabled: bool) -> None:
        """Grey out or re-enable the whole screen."""
        ...

    def notify_error(self, rs: ValidationResult) -> None:
        """Surface a failed refresh to the user."""
        ...

    def clear(self) -> None:
        """Empty both in-memory tables."""
        ...

    def notify_pomodoro_history_refresh(self, context: tuple[PomodoroHistoryRowState, ...]) -> None:
        """Replace the pomodoro history table's rows with `context`."""
        ...

    def notify_todo_history_refresh(self, context: tuple[TodoHistoryRowState, ...]) -> None:
        """Replace the TODO history table's rows with `context`."""
        ...


# EOF
