"""Orchestrates the pomodoro create/edit form (spec §2.3)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import time
from collections.abc import Callable
from typing import Final

from pomodoro.interfaces.i_pomodoro_edit_view import IPomodoroEditView
from pomodoro.interfaces.i_pomodoro_service import IPomodoroService
from pomodoro.interfaces.i_sound_service import ISoundService
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.shared import i18n_fra
from pomodoro.shared.errors.app_error import ErrorCodeApp
from pomodoro.shared.validation_result import ValidationResult

DEFAULT_NEW_POMODORO_DURATION_SECONDS: Final[int] = 5 * 60


class PomodoroEditPresenter:
    """Wires `IPomodoroEditView` callbacks to `IPomodoroService`/`ISoundService`."""

    def __init__(
        self, view: IPomodoroEditView, pomodoro_service: IPomodoroService, sound_service: ISoundService
    ) -> None:
        """Wire the view's callbacks and keep the injected collaborators."""
        self._view = view
        self._pomodoro_service = pomodoro_service
        self._sound_service = sound_service
        self._logger = logging.getLogger(self.__class__.__name__)
        self._id_pomodoro: str | None = None
        self._on_closed: Callable[[], None] | None = None
        self._wire_view()

    def _wire_view(self) -> None:
        """Bind every view callback to its handler."""
        self._view.bind_field_changed(self._handle_field_changed)
        self._view.bind_test_sound_clicked(self._handle_test_sound_clicked)
        self._view.bind_close_clicked(self._handle_close_clicked)

    def bind_closed(self, callback: Callable[[], None]) -> None:
        """Register the callback invoked when the user closes the edit form."""
        self._on_closed = callback

    def start_edit(self, id_pomodoro: str) -> None:
        """Load an existing pomodoro into the form (spec §2.2 '✎' button)."""
        pomodoro = self._pomodoro_service.get(id_pomodoro)
        if pomodoro is None:
            self._view.notify_error(ValidationResult.error(ErrorCodeApp.APP_9999))
            return
        self._id_pomodoro = id_pomodoro
        self._view.notify_refresh(pomodoro)

    def start_create(self) -> None:
        """Load a fresh, unsaved pomodoro into the form (spec §2.1 '+ Nouveau').

        Pre-fills the name and duration with sensible defaults rather than
        leaving them empty, so a brand-new pomodoro is already valid.
        """
        self._id_pomodoro = self._pomodoro_service.generate_id()
        self._view.clear()
        pomodoro = PomodoroModel.get_default()
        pomodoro.name = i18n_fra.FORM_DEFAULT_NAME
        pomodoro.duration_seconds = DEFAULT_NEW_POMODORO_DURATION_SECONDS
        self._view.notify_refresh(pomodoro)

    def _build_pomodoro(self, id_pomodoro: str) -> PomodoroModel:
        """Build a pomodoro from the view's current fields, preserving other state."""
        state = self._view.snapshot()
        existing = self._pomodoro_service.get(id_pomodoro)
        pomodoro = existing if existing is not None else PomodoroModel.get_default()
        pomodoro.id_pomodoro = id_pomodoro
        pomodoro.name = state.name
        pomodoro.duration_seconds = state.duration_seconds
        pomodoro.sound_path = state.sound_path
        pomodoro.sound_volume = state.sound_volume
        pomodoro.sound_repeat_count = state.sound_repeat_count
        pomodoro.sound_repeat_interval_seconds = state.sound_repeat_interval_seconds
        return pomodoro

    def _handle_field_changed(self) -> None:
        """Validate and persist the form's current content (debounced by the view)."""
        if self._id_pomodoro is None:
            return
        started_at = time.perf_counter()
        pomodoro = self._build_pomodoro(self._id_pomodoro)
        try:
            result = self._pomodoro_service.save(pomodoro)
        except Exception:  # last line of defense, AGENTS.md §12.3
            self._logger.exception("Action '%s' a échoué de manière inattendue", "modifier")
            self._view.notify_error(ValidationResult.error(ErrorCodeApp.APP_9999))
            return
        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        self._logger.info("Action '%s' terminée en %s ms", "modifier", elapsed_ms)
        if not result.is_valid:
            self._view.notify_error(result)
            return
        self._view.notify_saved()

    def _handle_test_sound_clicked(self) -> None:
        """Check availability, then ask the view to play a preview (spec §2.3)."""
        state = self._view.snapshot()
        result = self._sound_service.check_available(state.sound_path)
        if not result.is_valid:
            self._view.notify_error(result)
            return
        if state.sound_path is not None:
            self._view.play_preview(state.sound_path, state.sound_volume)

    def _handle_close_clicked(self) -> None:
        """Forward a 'Fermer' click to whichever presenter owns navigation."""
        self._id_pomodoro = None
        if self._on_closed is not None:
            self._on_closed()


# EOF
