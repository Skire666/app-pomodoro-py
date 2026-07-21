"""Read-only row snapshot for one pomodoro history table entry (spec §2.6)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from dataclasses import dataclass
from datetime import datetime

from pomodoro.shared.enums.pomodoro_history_status_enum import PomodoroHistoryStatusEnum


@dataclass(frozen=True, slots=True)
class PomodoroHistoryRowState:
    """One row of the pomodoro history table, as pushed by the Presenter into the View."""

    name: str
    is_source_deleted: bool
    executed_at: datetime
    planned_duration_seconds: int
    status: PomodoroHistoryStatusEnum


# EOF
