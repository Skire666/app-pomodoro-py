"""Contract for the pomodoro create/edit form (spec §2.3)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Callable
from typing import Protocol

from pomodoro.models.pomodoro_edit_view_state import PomodoroEditViewState
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.shared.validation_result import ValidationResult


class IPomodoroEditView(Protocol):
    """View contract for the create/edit form (AGENTS.md §13.4, spec §2.3)."""

    @property
    def is_dirty(self) -> bool:
        """True while the form holds an unsaved, in-progress edit."""
        ...

    @property
    def is_busy(self) -> bool:
        """True while a save or sound test is in flight."""
        ...

    @property
    def is_loading(self) -> bool:
        """True while the form is being populated from a loaded pomodoro."""
        ...

    def snapshot(self) -> PomodoroEditViewState:
        """Return the current form field values."""
        ...

    def set_enabled(self, enabled: bool) -> None:
        """Grey out or re-enable the whole form."""
        ...

    def notify_error(self, rs: ValidationResult) -> None:
        """Surface a failed validation or action to the user."""
        ...

    def clear(self) -> None:
        """Empty every form field."""
        ...

    def notify_refresh(self, context: PomodoroModel) -> None:
        """Populate the form with `context`'s current values."""
        ...

    def notify_saved(self) -> None:
        """Briefly show the '✓ Enregistré' indicator (spec §2.3)."""
        ...

    def play_preview(self, sound_path: str, volume: int) -> None:
        """Play a short preview of `sound_path` at `volume` (spec §2.3 'Tester')."""
        ...

    def bind_field_changed(self, callback: Callable[[], None]) -> None:
        """Register the callback fired once the view's own debounce settles."""
        ...

    def bind_test_sound_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when 'Tester' is clicked."""
        ...

    def bind_close_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when 'Fermer' is clicked."""
        ...


# EOF
