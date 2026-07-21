"""Sort modes offered above the pomodoro list."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from enum import Enum


class PomodoroSortModeEnum(Enum):
    """Enumerates the sort criteria available for the pomodoro list (see spec §2.1)."""

    E_UNSET = "UNSET"
    E_NAME = "NAME"
    E_DURATION = "DURATION"
    E_LAST_USED = "LAST_USED"
    E_UNKNOWN = "UNKNOWN"


# EOF
