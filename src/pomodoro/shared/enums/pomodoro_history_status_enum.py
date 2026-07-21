"""Outcome status of a completed pomodoro session, as recorded in history."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from enum import Enum


class PomodoroHistoryStatusEnum(Enum):
    """Enumerates the possible outcomes of a pomodoro session (see spec §2.6)."""

    E_UNSET = "UNSET"
    E_COMPLETED = "COMPLETED"
    E_INTERRUPTED = "INTERRUPTED"
    E_UNKNOWN = "UNKNOWN"


# EOF
