"""Business logic for the single active pomodoro session (spec §2.4)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import uuid
from datetime import UTC, datetime

from pomodoro.interfaces.i_config_repository import IConfigRepository
from pomodoro.models.active_session_model import ActiveSessionModel
from pomodoro.models.app_config_model import MAX_POMODORO_HISTORY_ENTRIES, AppConfigModel
from pomodoro.models.pomodoro_history_entry_model import PomodoroHistoryEntryModel
from pomodoro.shared.enums.pomodoro_history_status_enum import PomodoroHistoryStatusEnum
from pomodoro.shared.errors.app_error import ErrorCodeApp
from pomodoro.shared.errors.session_error import ErrorCodeSession
from pomodoro.shared.validation_result import ValidationResult


class SessionService:
    """Business rules for starting, pausing, and finishing a pomodoro session."""

    def __init__(self, config_repository: IConfigRepository) -> None:
        """Initialize the service with its injected repository."""
        self._config_repository = config_repository
        self._logger = logging.getLogger(self.__class__.__name__)

    def get_active(self) -> ActiveSessionModel | None:
        """Return the currently running session, or None if idle."""
        return AppConfigModel.instance().active_session

    def start(self, id_pomodoro: str) -> ValidationResult:
        """Start a new session for `id_pomodoro` (spec §2.4).

        Args:
            id_pomodoro: Identifier of the pomodoro to start.

        Returns:
            A successful ValidationResult once started, or a failed one if
            another session is already active or the pomodoro is unknown.
        """
        config = AppConfigModel.instance()
        if config.active_session is not None:
            return ValidationResult.error(ErrorCodeSession.SES_1001)
        pomodoro = config.pomodoros.read(id_pomodoro)
        if pomodoro is None:
            return ValidationResult.error(ErrorCodeApp.APP_9999)
        now = datetime.now(UTC)
        config.active_session = ActiveSessionModel(
            id_pomodoro=pomodoro.id_pomodoro,
            name_snapshot=pomodoro.name,
            planned_duration_seconds=pomodoro.duration_seconds,
            accumulated_seconds=0,
            is_paused=False,
            last_resumed_at=now,
            created_at=now,
            modified_at=now,
        )
        pomodoro.last_used_at = now
        pomodoro.mark_as_modified()
        self._persist()
        self._logger.debug("Session démarrée pour le pomodoro id=%s", id_pomodoro)
        return ValidationResult.ok()

    def pause(self) -> ValidationResult:
        """Pause the currently running session.

        Returns:
            A successful ValidationResult once paused, or a failed one if
            no session is active.
        """
        session = AppConfigModel.instance().active_session
        if session is None:
            return ValidationResult.error(ErrorCodeSession.SES_1002)
        session.pause(datetime.now(UTC))
        self._persist()
        return ValidationResult.ok()

    def resume(self) -> ValidationResult:
        """Resume the currently paused session.

        Returns:
            A successful ValidationResult once resumed, or a failed one if
            no session is active.
        """
        session = AppConfigModel.instance().active_session
        if session is None:
            return ValidationResult.error(ErrorCodeSession.SES_1002)
        session.resume(datetime.now(UTC))
        self._persist()
        return ValidationResult.ok()

    def reset(self) -> ValidationResult:
        """Reset the current session's countdown to the full planned duration.

        Returns:
            A successful ValidationResult once reset, or a failed one if
            no session is active.
        """
        session = AppConfigModel.instance().active_session
        if session is None:
            return ValidationResult.error(ErrorCodeSession.SES_1002)
        session.reset(datetime.now(UTC))
        self._persist()
        return ValidationResult.ok()

    def stop_interrupted(self) -> ValidationResult:
        """Stop the current session early, recording it as interrupted (spec §2.4).

        Returns:
            A successful ValidationResult once recorded, or a failed one if
            no session is active.
        """
        return self._finish(PomodoroHistoryStatusEnum.E_INTERRUPTED)

    def complete(self) -> ValidationResult:
        """Record the current session as completed, having reached 00:00:00.

        Returns:
            A successful ValidationResult once recorded, or a failed one if
            no session is active.
        """
        return self._finish(PomodoroHistoryStatusEnum.E_COMPLETED)

    def _finish(self, status: PomodoroHistoryStatusEnum) -> ValidationResult:
        """Record the current session in history under `status`, then clear it."""
        config = AppConfigModel.instance()
        session = config.active_session
        if session is None:
            return ValidationResult.error(ErrorCodeSession.SES_1002)
        entry = PomodoroHistoryEntryModel(
            id_history_entry=str(uuid.uuid4()),
            id_pomodoro=session.id_pomodoro,
            name_snapshot=session.name_snapshot,
            executed_at=session.created_at,
            planned_duration_seconds=session.planned_duration_seconds,
            status=status,
        )
        config.pomodoro_history.create(entry)
        config.pomodoro_history.purge(MAX_POMODORO_HISTORY_ENTRIES)
        config.active_session = None
        self._persist()
        self._logger.debug("Session terminée (%s) pour id=%s", status.value, entry.id_pomodoro)
        return ValidationResult.ok()

    def _persist(self) -> None:
        """Save the current singleton configuration through the repository."""
        self._config_repository.save(AppConfigModel.instance())


# EOF
