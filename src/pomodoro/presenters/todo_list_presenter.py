"""Orchestrates a pomodoro's TODO list (spec §2.5)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import time
from collections.abc import Callable

from pomodoro.interfaces.i_todo_list_view import ITodoListView
from pomodoro.interfaces.i_todo_service import ITodoService
from pomodoro.models.todo_item_model import TodoItemModel
from pomodoro.models.todo_row_state import TodoRowState
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum
from pomodoro.shared.errors.app_error import ErrorCodeApp
from pomodoro.shared.validation_result import ValidationResult


class TodoListPresenter:
    """Wires `ITodoListView` callbacks to `ITodoService` for one pomodoro at a time."""

    def __init__(self, view: ITodoListView, todo_service: ITodoService) -> None:
        """Wire the view's callbacks and keep the injected collaborator."""
        self._view = view
        self._todo_service = todo_service
        self._logger = logging.getLogger(self.__class__.__name__)
        self._id_pomodoro: str | None = None
        self._last_deleted: TodoItemModel | None = None
        self._wire_view()

    def _wire_view(self) -> None:
        """Bind every view callback to its handler."""
        self._view.bind_add_item_requested(self._handle_add_item_requested)
        self._view.bind_item_renamed(self._handle_item_renamed)
        self._view.bind_item_state_changed(self._handle_item_state_changed)
        self._view.bind_item_duplicate_clicked(self._handle_item_duplicate_clicked)
        self._view.bind_item_delete_clicked(self._handle_item_delete_clicked)
        self._view.bind_delete_list_clicked(self._handle_delete_list_clicked)
        self._view.bind_undo_delete_clicked(self._handle_undo_delete_clicked)

    def show_for_pomodoro(self, id_pomodoro: str) -> None:
        """Scope the presenter to `id_pomodoro` and refresh the view (spec §2.2 'TODO' tab)."""
        self._id_pomodoro = id_pomodoro
        self._last_deleted = None
        self.refresh()

    def refresh(self) -> None:
        """Reload the TODO items for the current pomodoro and push them into the view."""
        if self._id_pomodoro is None:
            self._view.notify_refresh(())
            return
        items = self._todo_service.list_for_pomodoro(self._id_pomodoro)
        self._view.notify_refresh(self._to_rows(items))

    @staticmethod
    def _to_rows(items: tuple[TodoItemModel, ...]) -> tuple[TodoRowState, ...]:
        """Convert domain models into read-only row states for the view."""
        return tuple(
            TodoRowState(id_todo_item=item.id_todo_item, label=item.label, state=item.state) for item in items
        )

    def _handle_add_item_requested(self, label: str) -> None:
        """Add a new item to the current pomodoro's list."""
        if self._id_pomodoro is None:
            return
        id_pomodoro = self._id_pomodoro
        self._run_action("ajouter", lambda: self._todo_service.add_item(id_pomodoro, label))

    def _handle_item_renamed(self, id_todo_item: str, label: str) -> None:
        """Rename an item in place."""
        self._run_action("renommer", lambda: self._todo_service.rename_item(id_todo_item, label))

    def _handle_item_state_changed(self, id_todo_item: str, new_state: TodoStateEnum) -> None:
        """Change an item's state and record the transition in history."""
        self._run_action("changer_etat", lambda: self._todo_service.change_state(id_todo_item, new_state))

    def _handle_item_duplicate_clicked(self, id_todo_item: str) -> None:
        """Duplicate an item, resetting its state (spec §2.5)."""
        self._run_action("dupliquer", lambda: self._duplicate(id_todo_item))

    def _duplicate(self, id_todo_item: str) -> ValidationResult:
        """Duplicate `id_todo_item`, reporting failure if it no longer exists."""
        clone = self._todo_service.duplicate_item(id_todo_item)
        if clone is None:
            return ValidationResult.error(ErrorCodeApp.APP_9999)
        return ValidationResult.ok()

    def _handle_item_delete_clicked(self, id_todo_item: str) -> None:
        """Delete a single item without confirmation, keeping it for undo (spec §2.5)."""
        deleted = self._todo_service.delete_item(id_todo_item)
        if deleted is None:
            self._view.notify_error(ValidationResult.error(ErrorCodeApp.APP_9999))
            return
        self._last_deleted = deleted
        self.refresh()
        self._view.notify_item_deleted(deleted.label)

    def _handle_undo_delete_clicked(self) -> None:
        """Restore the most recently deleted item, if any (spec §2.5 toast)."""
        if self._last_deleted is None:
            return
        item = self._last_deleted
        self._last_deleted = None
        self._run_action("annuler_suppression", lambda: self._todo_service.restore_item(item))

    def _handle_delete_list_clicked(self) -> None:
        """Delete every item for the current pomodoro (confirmed by the view beforehand)."""
        if self._id_pomodoro is None:
            return
        id_pomodoro = self._id_pomodoro
        self._run_action("supprimer_liste", lambda: self._delete_list(id_pomodoro))

    def _delete_list(self, id_pomodoro: str) -> ValidationResult:
        """Delete every TODO item for `id_pomodoro`."""
        self._todo_service.delete_list(id_pomodoro)
        return ValidationResult.ok()

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
