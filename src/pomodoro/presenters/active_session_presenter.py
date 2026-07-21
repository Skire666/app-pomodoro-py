"""Orchestrates the active pomodoro session screen (spec §2.4)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
from collections.abc import Callable
from datetime import UTC, datetime

from pomodoro.interfaces.i_active_session_view import IActiveSessionView
from pomodoro.interfaces.i_pomodoro_service import IPomodoroService
from pomodoro.interfaces.i_session_service import ISessionService
from pomodoro.models.active_session_model import ActiveSessionModel
from pomodoro.models.active_session_view_state import ActiveSessionViewState
from pomodoro.shared.errors.app_error import ErrorCodeApp
from pomodoro.shared.validation_result import ValidationResult


class ActiveSessionPresenter:
    """Wires `IActiveSessionView` callbacks to `ISessionService`/`IPomodoroService`."""

    def __init__(
        self, view: IActiveSessionView, session_service: ISessionService, pomodoro_service: IPomodoroService
    ) -> None:
        """Wire the view's callbacks and keep the injected collaborators."""
        self._view = view
        self._session_service = session_service
        self._pomodoro_service = pomodoro_service
        self._logger = logging.getLogger(self.__class__.__name__)
        self._id_pomodoro: str | None = None
        self._on_completed: Callable[[str], None] | None = None
        self._on_edit_requested: Callable[[str], None] | None = None
        self._on_back_to_list: Callable[[], None] | None = None
        self._wire_view()

    def _wire_view(self) -> None:
        """Bind every view callback to its handler."""
        self._view.bind_tick_requested(self._handle_tick)
        self._view.bind_edit_clicked(self._handle_edit_clicked)
        self._view.bind_play_clicked(self._handle_play_clicked)
        self._view.bind_pause_clicked(self._handle_pause_clicked)
        self._view.bind_reset_clicked(self._handle_reset_clicked)
        self._view.bind_restart_clicked(self._handle_restart_clicked)
        self._view.bind_back_to_list_clicked(self._handle_back_to_list_clicked)

    def bind_completed(self, callback: Callable[[str], None]) -> None:
        """Register the callback invoked once the session completes naturally.

        Args:
            callback: Invoked with the completed pomodoro's name, so the
                composition root can raise a desktop notification (spec §3.2).
        """
        self._on_completed = callback

    def bind_edit_requested(self, callback: Callable[[str], None]) -> None:
        """Register the callback invoked when the user requests to edit the pomodoro."""
        self._on_edit_requested = callback

    def bind_back_to_list_requested(self, callback: Callable[[], None]) -> None:
        """Register the callback invoked when 'Retour à la liste' is clicked."""
        self._on_back_to_list = callback

    def show(self) -> None:
        """Load the currently active session into the view (spec §2.4)."""
        session = self._session_service.get_active()
        if session is None:
            self._view.notify_error(ValidationResult.error(ErrorCodeApp.APP_9999))
            return
        self._id_pomodoro = session.id_pomodoro
        now = datetime.now(UTC)
        self._view.notify_refresh(
            ActiveSessionViewState(
                name=session.name_snapshot,
                planned_duration_seconds=session.planned_duration_seconds,
                remaining_seconds=session.remaining_seconds(now),
                is_paused=session.is_paused,
            )
        )

    def _handle_tick(self) -> None:
        """React to the view's once-a-second timer (spec §2.4, view-owned QTimer)."""
        session = self._session_service.get_active()
        if session is None:
            return
        now = datetime.now(UTC)
        self._view.notify_tick(session.remaining_seconds(now), session.is_paused)
        if session.is_complete(now):
            self._handle_natural_completion(session)

    def _handle_natural_completion(self, session: ActiveSessionModel) -> None:
        """Finish a session that reached 00:00:00: sound, history, and UI state (spec §2.4)."""
        pomodoro = self._pomodoro_service.get(session.id_pomodoro)
        result = self._session_service.complete()
        if not result.is_valid:
            return
        if pomodoro is not None and pomodoro.sound_path is not None:
            self._view.play_completion_sound(
                pomodoro.sound_path,
                pomodoro.sound_volume,
                pomodoro.sound_repeat_count,
                pomodoro.sound_repeat_interval_seconds,
            )
        name = pomodoro.name if pomodoro is not None else session.name_snapshot
        self._view.notify_completed(name)
        if self._on_completed is not None:
            self._on_completed(name)

    def _handle_edit_clicked(self) -> None:
        """Forward an 'Edit' click to whichever presenter owns editing."""
        if self._id_pomodoro is not None and self._on_edit_requested is not None:
            self._on_edit_requested(self._id_pomodoro)

    def _handle_play_clicked(self) -> None:
        """Resume the paused session and refresh the display immediately."""
        result = self._session_service.resume()
        if not result.is_valid:
            self._view.notify_error(result)
            return
        self._refresh_display()

    def _handle_pause_clicked(self) -> None:
        """Pause the running session and refresh the display immediately."""
        result = self._session_service.pause()
        if not result.is_valid:
            self._view.notify_error(result)
            return
        self._refresh_display()

    def _handle_reset_clicked(self) -> None:
        """Reset the countdown to the full duration, keeping the running/paused state."""
        result = self._session_service.reset()
        if not result.is_valid:
            self._view.notify_error(result)
            return
        self._refresh_display()

    def _refresh_display(self) -> None:
        """Push the current remaining time/paused state into the view immediately."""
        session = self._session_service.get_active()
        if session is None:
            return
        now = datetime.now(UTC)
        self._view.notify_tick(session.remaining_seconds(now), session.is_paused)

    def _handle_restart_clicked(self) -> None:
        """Restart the same pomodoro from the 'Terminé ✓' state (spec §2.4 'Relancer')."""
        if self._id_pomodoro is None:
            return
        result = self._session_service.start(self._id_pomodoro)
        if not result.is_valid:
            self._view.notify_error(result)
            return
        self.show()

    def _handle_back_to_list_clicked(self) -> None:
        """Forward a 'Retour à la liste' click to whichever presenter owns navigation."""
        if self._on_back_to_list is not None:
            self._on_back_to_list()


# EOF
