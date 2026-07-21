"""Read-only snapshot of the create/edit form's fields (spec §2.3)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PomodoroEditViewState:
    """The current form field values, as captured by `IPomodoroEditView.snapshot`."""

    name: str
    duration_seconds: int
    sound_path: str | None
    sound_volume: int
    sound_repeat_count: int
    sound_repeat_interval_seconds: int


# EOF
