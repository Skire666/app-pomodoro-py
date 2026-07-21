"""Lifecycle states of a TODO item attached to a pomodoro."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from enum import Enum


class TodoStateEnum(Enum):
    """Enumerates the lifecycle states of a TODO item (see spec §2.5)."""

    E_UNSET = "UNSET"
    E_TODO = "TODO"
    E_IN_PROGRESS = "IN_PROGRESS"
    E_DONE = "DONE"
    E_CANCELLED = "CANCELLED"
    E_UNKNOWN = "UNKNOWN"


# EOF
