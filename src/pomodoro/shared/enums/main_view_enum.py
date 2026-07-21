"""Top-level navigation targets in the left-hand column (see spec §1)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from enum import Enum


class MainViewEnum(Enum):
    """Enumerates the main navigation sections of the application."""

    E_UNSET = "UNSET"
    E_POMODOROS = "POMODOROS"
    E_HISTORY = "HISTORY"
    E_UNKNOWN = "UNKNOWN"


# EOF
