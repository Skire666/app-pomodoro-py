"""Orchestrates the read-only history screen (spec §2.6)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import time

from pomodoro.interfaces.i_history_service import IHistoryService
from pomodoro.interfaces.i_history_view import IHistoryView
from pomodoro.interfaces.i_pomodoro_service import IPomodoroService
from pomodoro.models.pomodoro_history_entry_model import PomodoroHistoryEntryModel
from pomodoro.models.pomodoro_history_row_state import PomodoroHistoryRowState
from pomodoro.models.todo_history_entry_model import TodoHistoryEntryModel
from pomodoro.models.todo_history_row_state import TodoHistoryRowState
from pomodoro.shared.errors.app_error import ErrorCodeApp
from pomodoro.shared.validation_result import ValidationResult


class HistoryPresenter:
    """Loads pomodoro/TODO history from the services and pushes it into the view."""

    def __init__(
        self, view: IHistoryView, history_service: IHistoryService, pomodoro_service: IPomodoroService
    ) -> None:
        """Keep the view and its injected collaborators."""
        self._view = view
        self._history_service = history_service
        self._pomodoro_service = pomodoro_service
        self._logger = logging.getLogger(self.__class__.__name__)

    def refresh(self) -> None:
        """Reload both history tables and push them into the view (spec §2.6)."""
        started_at = time.perf_counter()
        try:
            self._refresh_pomodoro_history()
            self._refresh_todo_history()
        except Exception:  # last line of defense, AGENTS.md §12.3
            self._logger.exception("Action '%s' a échoué de manière inattendue", "actualiser_historique")
            self._view.notify_error(ValidationResult.error(ErrorCodeApp.APP_9999))
            return
        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        self._logger.info("Action '%s' terminée en %s ms", "actualiser_historique", elapsed_ms)

    def _refresh_pomodoro_history(self) -> None:
        """Load pomodoro session history and push it into the view."""
        entries = self._history_service.list_pomodoro_history()
        rows = tuple(self._to_pomodoro_row(entry) for entry in entries)
        self._view.notify_pomodoro_history_refresh(rows)

    def _to_pomodoro_row(self, entry: PomodoroHistoryEntryModel) -> PomodoroHistoryRowState:
        """Convert one history entry, resolving whether its source still exists (spec §2.6)."""
        return PomodoroHistoryRowState(
            name=entry.name_snapshot,
            is_source_deleted=self._pomodoro_service.get(entry.id_pomodoro) is None,
            executed_at=entry.executed_at,
            planned_duration_seconds=entry.planned_duration_seconds,
            status=entry.status,
        )

    def _refresh_todo_history(self) -> None:
        """Load TODO state-change history and push it into the view."""
        entries = self._history_service.list_todo_history()
        rows = tuple(self._to_todo_row(entry) for entry in entries)
        self._view.notify_todo_history_refresh(rows)

    @staticmethod
    def _to_todo_row(entry: TodoHistoryEntryModel) -> TodoHistoryRowState:
        """Convert one TODO history entry into a row state."""
        return TodoHistoryRowState(
            label=entry.label_snapshot,
            pomodoro_name=entry.pomodoro_name_snapshot,
            old_state=entry.old_state,
            new_state=entry.new_state,
            changed_at=entry.changed_at,
        )


# EOF
