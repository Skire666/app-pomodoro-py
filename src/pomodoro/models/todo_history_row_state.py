"""Read-only row snapshot for one TODO history table entry (spec §2.6)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from dataclasses import dataclass
from datetime import datetime

from pomodoro.shared.enums.todo_state_enum import TodoStateEnum


@dataclass(frozen=True, slots=True)
class TodoHistoryRowState:
    """One row of the TODO history table, as pushed by the Presenter into the View."""

    label: str
    pomodoro_name: str
    old_state: TodoStateEnum
    new_state: TodoStateEnum
    changed_at: datetime


# EOF
