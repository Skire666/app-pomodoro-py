"""Read-only row snapshot for one pomodoro card in the list (spec §2.1)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PomodoroRowState:
    """One row of the pomodoro list, as pushed by the Presenter into the View.

    A frozen value object (AGENTS.md §3.2), not a persisted entity: it
    carries no `id_xxxx`/`validate`/`copy` contract of its own.
    """

    id_pomodoro: str
    name: str
    duration_seconds: int


# EOF
