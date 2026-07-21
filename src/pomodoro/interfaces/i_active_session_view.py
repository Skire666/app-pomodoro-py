"""Contract for the active pomodoro session screen (spec §2.4)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Callable
from typing import Protocol

from pomodoro.models.active_session_view_state import ActiveSessionViewState
from pomodoro.shared.validation_result import ValidationResult


class IActiveSessionView(Protocol):
    """View contract for the countdown screen (AGENTS.md §13.4, spec §2.4).

    Driven by its own once-a-second `QTimer` tick (AGENTS.md §16.6) rather
    than a holistic form, so this contract has no meaningful `snapshot()`
    and omits it.
    """

    @property
    def is_busy(self) -> bool:
        """True while a play/pause/reset action is in flight."""
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
        """Reset the screen to its idle, pre-session appearance."""
        ...

    def notify_refresh(self, context: ActiveSessionViewState) -> None:
        """Display `context`'s current values when the session is first shown."""
        ...

    def notify_tick(self, remaining_seconds: int, is_paused: bool) -> None:
        """Update the countdown display for one second of elapsed time."""
        ...

    def play_completion_sound(
        self, sound_path: str, volume: int, repeat_count: int, repeat_interval_seconds: int
    ) -> None:
        """Play the configured completion sound, repeated per the pomodoro's settings."""
        ...

    def stop_completion_sound(self) -> None:
        """Silence the completion alarm immediately and cancel any pending repetition."""
        ...

    def bind_tick_requested(self, callback: Callable[[], None]) -> None:
        """Register the callback fired once a second by the view's own timer."""
        ...

    def bind_edit_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when 'Edit' is clicked."""
        ...

    def bind_play_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when 'Play' is clicked (greyed out while running)."""
        ...

    def bind_pause_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when '⏸ Pause' is clicked (greyed out while paused)."""
        ...

    def bind_reset_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when '⟲ Reset' is clicked."""
        ...


# EOF
