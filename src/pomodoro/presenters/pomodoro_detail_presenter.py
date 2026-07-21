"""Orchestrates the read-only pomodoro detail screen (spec §2.2)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Callable

from pomodoro.interfaces.i_pomodoro_detail_view import IPomodoroDetailView
from pomodoro.interfaces.i_pomodoro_service import IPomodoroService
from pomodoro.interfaces.i_todo_service import ITodoService
from pomodoro.models.pomodoro_detail_view_state import PomodoroDetailViewState
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.shared.errors.app_error import ErrorCodeApp
from pomodoro.shared.validation_result import ValidationResult


class PomodoroDetailPresenter:
    """Wires `IPomodoroDetailView` callbacks to `IPomodoroService`/`ITodoService`."""

    def __init__(
        self, view: IPomodoroDetailView, pomodoro_service: IPomodoroService, todo_service: ITodoService
    ) -> None:
        """Wire the view's callbacks and keep the injected collaborators."""
        self._view = view
        self._pomodoro_service = pomodoro_service
        self._todo_service = todo_service
        self._id_pomodoro: str | None = None
        self._on_edit_requested: Callable[[str], None] | None = None
        self._on_start_requested: Callable[[str], None] | None = None
        self._wire_view()

    def _wire_view(self) -> None:
        """Bind every view callback to its handler."""
        self._view.bind_edit_clicked(self._handle_edit_clicked)
        self._view.bind_start_clicked(self._handle_start_clicked)

    def bind_edit_requested(self, callback: Callable[[str], None]) -> None:
        """Register the callback invoked when the user requests to edit the pomodoro."""
        self._on_edit_requested = callback

    def bind_start_requested(self, callback: Callable[[str], None]) -> None:
        """Register the callback invoked when the user requests a session start."""
        self._on_start_requested = callback

    def show(self, id_pomodoro: str) -> None:
        """Scope the presenter to `id_pomodoro` and refresh the view (spec §2.1 selection)."""
        self._id_pomodoro = id_pomodoro
        self.refresh()

    def refresh(self) -> None:
        """Reload the current pomodoro from the services and push it into the view."""
        if self._id_pomodoro is None:
            return
        pomodoro = self._pomodoro_service.get(self._id_pomodoro)
        if pomodoro is None:
            self._view.notify_error(ValidationResult.error(ErrorCodeApp.APP_9999))
            return
        todo_count = self._todo_service.count_active_for_pomodoro(self._id_pomodoro)
        self._view.notify_refresh(self._to_state(pomodoro, todo_count))

    @staticmethod
    def _to_state(pomodoro: PomodoroModel, todo_count: int) -> PomodoroDetailViewState:
        """Combine a pomodoro and its active TODO count into a display state."""
        return PomodoroDetailViewState(
            id_pomodoro=pomodoro.id_pomodoro,
            name=pomodoro.name,
            duration_seconds=pomodoro.duration_seconds,
            sound_path=pomodoro.sound_path,
            sound_volume=pomodoro.sound_volume,
            sound_repeat_count=pomodoro.sound_repeat_count,
            sound_repeat_interval_seconds=pomodoro.sound_repeat_interval_seconds,
            todo_count=todo_count,
        )

    def _handle_edit_clicked(self) -> None:
        """Forward a '✎' click to whichever presenter owns editing."""
        if self._id_pomodoro is not None and self._on_edit_requested is not None:
            self._on_edit_requested(self._id_pomodoro)

    def _handle_start_clicked(self) -> None:
        """Forward a 'Démarrer' click to whichever presenter owns sessions."""
        if self._id_pomodoro is not None and self._on_start_requested is not None:
            self._on_start_requested(self._id_pomodoro)


# EOF
