"""Contract for the read-only pomodoro detail screen (spec §2.2)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Callable
from typing import Protocol

from pomodoro.models.pomodoro_detail_view_state import PomodoroDetailViewState
from pomodoro.shared.validation_result import ValidationResult


class IPomodoroDetailView(Protocol):
    """View contract for the pomodoro detail screen (AGENTS.md §13.4, spec §2.2).

    Purely a read-only display with no editable form, so this contract has
    no meaningful `snapshot()` or `is_dirty` to offer and omits them.
    """

    @property
    def is_busy(self) -> bool:
        """True while a triggered action is in flight."""
        ...

    @property
    def is_loading(self) -> bool:
        """True while the screen is loading or building itself."""
        ...

    def set_enabled(self, enabled: bool) -> None:
        """Grey out or re-enable the whole screen."""
        ...

    def notify_error(self, rs: ValidationResult) -> None:
        """Surface a failed action to the user."""
        ...

    def clear(self) -> None:
        """Empty the displayed content."""
        ...

    def notify_refresh(self, context: PomodoroDetailViewState) -> None:
        """Display `context`'s current values."""
        ...

    def bind_edit_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when '✎' is clicked."""
        ...

    def bind_start_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when '▶ Démarrer' is clicked."""
        ...


# EOF
