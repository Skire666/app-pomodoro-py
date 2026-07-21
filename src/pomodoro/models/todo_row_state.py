"""Read-only row snapshot for one TODO item line (spec §2.5)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from dataclasses import dataclass

from pomodoro.shared.enums.todo_state_enum import TodoStateEnum


@dataclass(frozen=True, slots=True)
class TodoRowState:
    """One row of a pomodoro's TODO list, as pushed by the Presenter into the View."""

    id_todo_item: str
    label: str
    state: TodoStateEnum


# EOF
