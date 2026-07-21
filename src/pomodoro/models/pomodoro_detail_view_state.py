"""Read-only snapshot of the pomodoro detail screen (spec §2.2)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PomodoroDetailViewState:
    """The pomodoro currently shown by `IPomodoroDetailView`, with its TODO count."""

    id_pomodoro: str
    name: str
    duration_seconds: int
    sound_path: str | None
    sound_volume: int
    sound_repeat_count: int
    sound_repeat_interval_seconds: int
    todo_count: int


# EOF
