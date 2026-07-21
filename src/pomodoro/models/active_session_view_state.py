"""Read-only snapshot of the active session screen, at load time (spec §2.4)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ActiveSessionViewState:
    """The session's name, planned duration, and remaining time, as first shown."""

    name: str
    planned_duration_seconds: int
    remaining_seconds: int
    is_paused: bool


# EOF
