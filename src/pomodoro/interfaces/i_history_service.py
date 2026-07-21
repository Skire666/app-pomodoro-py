"""Contract for the pomodoro/TODO history business-logic service."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from datetime import datetime
from typing import Protocol

from pomodoro.models.pomodoro_history_entry_model import PomodoroHistoryEntryModel
from pomodoro.models.todo_history_entry_model import TodoHistoryEntryModel
from pomodoro.shared.enums.pomodoro_history_status_enum import PomodoroHistoryStatusEnum


class IHistoryService(Protocol):
    """Service contract for pomodoro session history and TODO change history (spec §2.6)."""

    @staticmethod
    def generate_id() -> str:
        """Generate a unique identifier for a new pomodoro history entry."""
        ...

    def list_pomodoro_history(self) -> tuple[PomodoroHistoryEntryModel, ...]:
        """List pomodoro session history, most recent first."""
        ...

    def list_todo_history(self) -> tuple[TodoHistoryEntryModel, ...]:
        """List TODO state-change history, most recent first."""
        ...

    def record_pomodoro_session(
        self,
        id_pomodoro: str,
        name_snapshot: str,
        executed_at: datetime,
        planned_duration_seconds: int,
        status: PomodoroHistoryStatusEnum,
    ) -> PomodoroHistoryEntryModel:
        """Record one finished pomodoro session and purge overflow entries.

        Args:
            id_pomodoro: Identifier of the source pomodoro.
            name_snapshot: Name of the source pomodoro, frozen at execution time.
            executed_at: Timestamp at which the session started.
            planned_duration_seconds: Configured duration, in seconds.
            status: Outcome of the session (completed or interrupted).

        Returns:
            The recorded history entry.
        """
        ...


# EOF
