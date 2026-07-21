"""Orchestrates the pomodoro list screen (spec §2.1)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import time
from collections.abc import Callable

from pomodoro.interfaces.i_pomodoro_list_view import IPomodoroListView
from pomodoro.interfaces.i_pomodoro_service import IPomodoroService
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.models.pomodoro_row_state import PomodoroRowState
from pomodoro.shared.enums.pomodoro_sort_mode_enum import PomodoroSortModeEnum
from pomodoro.shared.errors.app_error import ErrorCodeApp
from pomodoro.shared.validation_result import ValidationResult


class PomodoroListPresenter:
    """Wires `IPomodoroListView` callbacks to `IPomodoroService` (spec §2.1)."""

    def __init__(self, view: IPomodoroListView, pomodoro_service: IPomodoroService) -> None:
        """Wire the view's callbacks and keep the injected collaborators.

        Args:
            view: The pomodoro list view to orchestrate.
            pomodoro_service: Business logic for pomodoro definitions.
        """
        self._view = view
        self._pomodoro_service = pomodoro_service
        self._logger = logging.getLogger(self.__class__.__name__)
        self._on_start_requested: Callable[[str], None] | None = None
        self._on_edit_requested: Callable[[str], None] | None = None
        self._on_new_requested: Callable[[], None] | None = None
        self._wire_view()

    def _wire_view(self) -> None:
        """Bind every view callback to its handler."""
        self._view.bind_search_changed(self._handle_search_changed)
        self._view.bind_sort_changed(self._handle_sort_changed)
        self._view.bind_new_clicked(self._handle_new_clicked)
        self._view.bind_item_start_clicked(self._handle_item_start_clicked)
        self._view.bind_item_edit_clicked(self._handle_item_edit_clicked)
        self._view.bind_item_duplicate_clicked(self._handle_item_duplicate_clicked)
        self._view.bind_item_delete_clicked(self._handle_item_delete_clicked)

    def bind_start_requested(self, callback: Callable[[str], None]) -> None:
        """Register the callback invoked when the user requests a session start."""
        self._on_start_requested = callback

    def bind_edit_requested(self, callback: Callable[[str], None]) -> None:
        """Register the callback invoked when the user requests to edit a pomodoro."""
        self._on_edit_requested = callback

    def bind_new_requested(self, callback: Callable[[], None]) -> None:
        """Register the callback invoked when the user requests a new pomodoro."""
        self._on_new_requested = callback

    def refresh(self) -> None:
        """Reload the pomodoro list from the service and push it into the view."""
        state = self._view.snapshot()
        pomodoros = self._pomodoro_service.list_all(state.search_text, state.sort_mode)
        self._view.notify_refresh(self._to_rows(pomodoros))

    @staticmethod
    def _to_rows(pomodoros: tuple[PomodoroModel, ...]) -> tuple[PomodoroRowState, ...]:
        """Convert domain models into read-only row states for the view."""
        return tuple(
            PomodoroRowState(
                id_pomodoro=pomodoro.id_pomodoro, name=pomodoro.name, duration_seconds=pomodoro.duration_seconds
            )
            for pomodoro in pomodoros
        )

    def _handle_search_changed(self, _search_text: str) -> None:
        """React to a search text change by refreshing the list."""
        self.refresh()

    def _handle_sort_changed(self, _sort_mode: PomodoroSortModeEnum) -> None:
        """React to a sort selection change by refreshing the list."""
        self.refresh()

    def _handle_new_clicked(self) -> None:
        """Forward a '+ Nouveau' click to whichever presenter owns creation."""
        if self._on_new_requested is not None:
            self._on_new_requested()

    def _handle_item_start_clicked(self, id_pomodoro: str) -> None:
        """Forward a 'Démarrer' click to whichever presenter owns sessions."""
        if self._on_start_requested is not None:
            self._on_start_requested(id_pomodoro)

    def _handle_item_edit_clicked(self, id_pomodoro: str) -> None:
        """Forward a 'Modifier' click to whichever presenter owns editing."""
        if self._on_edit_requested is not None:
            self._on_edit_requested(id_pomodoro)

    def _handle_item_duplicate_clicked(self, id_pomodoro: str) -> None:
        """Duplicate a pomodoro and refresh the list."""
        self._run_action("dupliquer", lambda: self._duplicate(id_pomodoro))

    def _duplicate(self, id_pomodoro: str) -> ValidationResult:
        """Duplicate `id_pomodoro`, reporting failure if it no longer exists."""
        clone = self._pomodoro_service.duplicate(id_pomodoro)
        if clone is None:
            return ValidationResult.error(ErrorCodeApp.APP_9999)
        return ValidationResult.ok()

    def _handle_item_delete_clicked(self, id_pomodoro: str) -> None:
        """Delete a pomodoro, regardless of any session state (spec §3.4).

        The view already obtained the user's yes/no confirmation before
        forwarding this click.
        """
        self._run_action("supprimer", lambda: self._pomodoro_service.delete(id_pomodoro))

    def _run_action(self, action_name: str, action: Callable[[], ValidationResult]) -> None:
        """Time, execute, and report the outcome of one user-triggered action."""
        started_at = time.perf_counter()
        try:
            result = action()
        except Exception:  # last line of defense, AGENTS.md §12.3
            self._logger.exception("Action '%s' a échoué de manière inattendue", action_name)
            self._view.notify_error(ValidationResult.error(ErrorCodeApp.APP_9999))
            return
        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        self._logger.info("Action '%s' terminée en %s ms", action_name, elapsed_ms)
        if not result.is_valid:
            self._view.notify_error(result)
            return
        self.refresh()


# EOF
