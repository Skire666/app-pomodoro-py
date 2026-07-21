"""Read-only snapshot of the pomodoro list screen's controls (spec §2.1)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from dataclasses import dataclass

from pomodoro.shared.enums.pomodoro_sort_mode_enum import PomodoroSortModeEnum


@dataclass(frozen=True, slots=True)
class PomodoroListViewState:
    """The current search/filter/sort controls, as captured by `IPomodoroListView.snapshot`."""

    search_text: str
    sort_mode: PomodoroSortModeEnum


# EOF
