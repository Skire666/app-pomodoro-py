"""Read access to pomodoro/TODO history, and pomodoro session recording (spec §2.6)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import uuid
from datetime import datetime

from pomodoro.interfaces.i_config_repository import IConfigRepository
from pomodoro.models.app_config_model import MAX_POMODORO_HISTORY_ENTRIES, AppConfigModel
from pomodoro.models.pomodoro_history_entry_model import PomodoroHistoryEntryModel
from pomodoro.models.todo_history_entry_model import TodoHistoryEntryModel
from pomodoro.shared.enums.pomodoro_history_status_enum import PomodoroHistoryStatusEnum


class HistoryService:
    """Business rules for pomodoro session history and TODO change history."""

    def __init__(self, config_repository: IConfigRepository) -> None:
        """Initialize the service with its injected repository."""
        self._config_repository = config_repository
        self._logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def generate_id() -> str:
        """Generate a unique identifier for a new pomodoro history entry."""
        return str(uuid.uuid4())

    def list_pomodoro_history(self) -> tuple[PomodoroHistoryEntryModel, ...]:
        """List pomodoro session history, most recent first (spec §2.6)."""
        return AppConfigModel.instance().pomodoro_history.search()

    def list_todo_history(self) -> tuple[TodoHistoryEntryModel, ...]:
        """List TODO state-change history, most recent first (spec §2.6)."""
        return AppConfigModel.instance().todo_history.search()

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
        entry = PomodoroHistoryEntryModel(
            id_history_entry=self.generate_id(),
            id_pomodoro=id_pomodoro,
            name_snapshot=name_snapshot,
            executed_at=executed_at,
            planned_duration_seconds=planned_duration_seconds,
            status=status,
        )
        history = AppConfigModel.instance().pomodoro_history
        history.create(entry)
        history.purge(MAX_POMODORO_HISTORY_ENTRIES)
        self._config_repository.save(AppConfigModel.instance())
        self._logger.debug("Session de pomodoro enregistrée dans l'historique : id=%s", entry.id_history_entry)
        return entry


# EOF
