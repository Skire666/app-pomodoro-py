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
        self._is_ringing = False
        self._on_edit_requested: Callable[[str], None] | None = None
        self._wire_view()

    def _wire_view(self) -> None:
        """Bind every view callback to its handler."""
        self._view.bind_tick_requested(self._handle_tick)
        self._view.bind_edit_clicked(self._handle_edit_clicked)
        self._view.bind_play_clicked(self._handle_play_clicked)
        self._view.bind_pause_clicked(self._handle_pause_clicked)
        self._view.bind_reset_clicked(self._handle_reset_clicked)

    def bind_edit_requested(self, callback: Callable[[str], None]) -> None:
        """Register the callback invoked when the user requests to edit the pomodoro."""
        self._on_edit_requested = callback

    def show(self) -> None:
        """Load the currently active session into the view (spec §2.4)."""
        session = self._session_service.get_active()
        if session is None:
            self._view.notify_error(ValidationResult.error(ErrorCodeApp.APP_9999))
            return
        self._id_pomodoro = session.id_pomodoro
        self._is_ringing = False
        now = datetime.now(UTC)
        self._view.notify_refresh(
            ActiveSessionViewState(
                name=session.name_snapshot,
                planned_duration_seconds=session.planned_duration_seconds,
                remaining_seconds=session.remaining_seconds(now),
                is_paused=session.is_paused,
            )
        )
        self._maybe_start_ringing(session, now)

    def _handle_tick(self) -> None:
        """React to the view's once-a-second timer (spec §2.4, view-owned QTimer)."""
        session = self._session_service.get_active()
        if session is None:
            return
        now = datetime.now(UTC)
        self._view.notify_tick(session.remaining_seconds(now), session.is_paused)
        self._maybe_start_ringing(session, now)

    def _maybe_start_ringing(self, session: ActiveSessionModel, now: datetime) -> None:
        """Start the completion alarm the first time the countdown reaches 00:00:00.

        The countdown then keeps counting into the negative (spec §2.4): the
        screen stays put and the alarm just plays until the user acts on it
        (`stop_ringing`) or it exhausts its own repeat count.
        """
        if self._is_ringing or session.is_paused or not session.is_complete(now):
            return
        self._is_ringing = True
        pomodoro = self._pomodoro_service.get(session.id_pomodoro)
        if pomodoro is not None and pomodoro.sound_path is not None:
            self._view.play_completion_sound(
                pomodoro.sound_path,
                pomodoro.sound_volume,
                pomodoro.sound_repeat_count,
                pomodoro.sound_repeat_interval_seconds,
            )

    def stop_ringing(self) -> None:
        """Silence an in-progress alarm (spec §2.4 'coupe le minuteur').

        Used both when the user acts on the running screen while the alarm
        rings (Edit/Play/Pause/Reset) and when another pomodoro is started
        over this one (session-switch confirmation): either way, only the
        alarm sound needs cutting off, nothing else changes.
        """
        if self._is_ringing:
            self._view.stop_completion_sound()
            self._is_ringing = False

    def _handle_edit_clicked(self) -> None:
        """Forward an 'Edit' click to whichever presenter owns editing.

        Also silences a ringing alarm first, so leaving for the edit screen
        never leaves the sound running unattended in the background.
        """
        self.stop_ringing()
        if self._id_pomodoro is not None and self._on_edit_requested is not None:
            self._on_edit_requested(self._id_pomodoro)

    def _handle_play_clicked(self) -> None:
        """Resume the paused session and refresh the display immediately.

        Also silences a ringing alarm in the same click (spec §2.4 'coupe
        le minuteur'): the user should not have to click twice.
        """
        self.stop_ringing()
        result = self._session_service.resume()
        if not result.is_valid:
            self._view.notify_error(result)
            return
        self._refresh_display()

    def _handle_pause_clicked(self) -> None:
        """Pause the running session and refresh the display immediately.

        Also silences a ringing alarm in the same click (spec §2.4 'coupe
        le minuteur'): the user should not have to click twice.
        """
        self.stop_ringing()
        result = self._session_service.pause()
        if not result.is_valid:
            self._view.notify_error(result)
            return
        self._refresh_display()

    def _handle_reset_clicked(self) -> None:
        """Reset the countdown to the full duration, keeping the running/paused state.

        Also silences a ringing alarm in the same click (spec §2.4 'coupe
        le minuteur'): the user should not have to click twice.
        """
        self.stop_ringing()
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


# EOF
