"""Business logic for the TODO list attached to a pomodoro (spec §2.5, §2.6)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import uuid
from datetime import UTC, datetime

from pomodoro.interfaces.i_config_repository import IConfigRepository
from pomodoro.models.app_config_model import MAX_TODO_HISTORY_ENTRIES, AppConfigModel
from pomodoro.models.todo_history_entry_model import TodoHistoryEntryModel
from pomodoro.models.todo_item_model import TodoItemModel
from pomodoro.shared.enums.copy_mode_enum import CopyModeEnum
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum
from pomodoro.shared.errors.todo_error import ErrorCodeTodo
from pomodoro.shared.i18n_fra import TODO_DUPLICATE_SUFFIX
from pomodoro.shared.validation_result import ValidationResult


class TodoService:
    """Business rules for a pomodoro's TODO list."""

    def __init__(self, config_repository: IConfigRepository) -> None:
        """Initialize the service with its injected repository."""
        self._config_repository = config_repository
        self._logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def generate_id() -> str:
        """Generate a unique identifier for a new TODO item."""
        return str(uuid.uuid4())

    def list_for_pomodoro(self, id_pomodoro: str) -> tuple[TodoItemModel, ...]:
        """List every TODO item belonging to `id_pomodoro`, in storage order."""
        return AppConfigModel.instance().todos.for_pomodoro(id_pomodoro)

    def count_active_for_pomodoro(self, id_pomodoro: str) -> int:
        """Count non-cancelled TODO items for `id_pomodoro` (spec §2.2 tab label)."""
        return AppConfigModel.instance().todos.count_active_for_pomodoro(id_pomodoro)

    def add_item(self, id_pomodoro: str, label: str) -> ValidationResult:
        """Create and persist a new TODO item (spec §2.5, initial state 'À faire').

        Args:
            id_pomodoro: Identifier of the owning pomodoro.
            label: Text label of the new item.

        Returns:
            A successful ValidationResult once persisted, or a failed one
            if the label is empty.
        """
        item = TodoItemModel.get_default()
        item.id_todo_item = self.generate_id()
        item.id_pomodoro = id_pomodoro
        item.label = label
        result = item.validate()
        if not result.is_valid:
            return result
        item.mark_as_created()
        AppConfigModel.instance().todos.create(item)
        self._persist()
        return ValidationResult.ok()

    def rename_item(self, id_todo_item: str, label: str) -> ValidationResult:
        """Rename a TODO item in place (spec §2.5 inline edit).

        Args:
            id_todo_item: Identifier of the item to rename.
            label: The new label.

        Returns:
            A successful ValidationResult once persisted, or a failed one
            if the item does not exist or the label is empty.
        """
        item = AppConfigModel.instance().todos.read(id_todo_item)
        if item is None:
            return ValidationResult.error(ErrorCodeTodo.TDI_9999)
        item.label = label
        result = item.validate()
        if not result.is_valid:
            return result
        item.mark_as_modified()
        self._persist()
        return ValidationResult.ok()

    def change_state(self, id_todo_item: str, new_state: TodoStateEnum) -> ValidationResult:
        """Change a TODO item's state and record it in history (spec §2.5, §2.6).

        Args:
            id_todo_item: Identifier of the item to update.
            new_state: The state to transition to.

        Returns:
            A successful ValidationResult once persisted, or a failed one
            if the item does not exist.
        """
        config = AppConfigModel.instance()
        item = config.todos.read(id_todo_item)
        if item is None:
            return ValidationResult.error(ErrorCodeTodo.TDI_9999)
        old_state = item.state
        if old_state is new_state:
            return ValidationResult.ok()
        pomodoro = config.pomodoros.read(item.id_pomodoro)
        item.state = new_state
        item.mark_as_modified()
        self._record_state_change(item, old_state, new_state, pomodoro_name=pomodoro.name if pomodoro else "")
        self._persist()
        return ValidationResult.ok()

    def duplicate_item(self, id_todo_item: str) -> TodoItemModel | None:
        """Duplicate a TODO item, resetting its state (spec §2.5).

        Args:
            id_todo_item: Identifier of the item to duplicate.

        Returns:
            The newly created copy, or None if `id_todo_item` does not exist.
        """
        source = AppConfigModel.instance().todos.read(id_todo_item)
        if source is None:
            return None
        clone = source.copy(CopyModeEnum.E_BUSINESS)
        clone.id_todo_item = self.generate_id()
        clone.label = f"{source.label}{TODO_DUPLICATE_SUFFIX}"
        clone.state = TodoStateEnum.E_TODO
        clone.mark_as_created()
        AppConfigModel.instance().todos.create(clone)
        self._persist()
        return clone

    def delete_item(self, id_todo_item: str) -> TodoItemModel | None:
        """Delete a single TODO item (spec §2.5, no confirmation required).

        Returns:
            The removed item, so the caller can offer an undo (spec §2.5
            toast), or None if no item matched `id_todo_item`.
        """
        item = AppConfigModel.instance().todos.read(id_todo_item)
        if item is None:
            return None
        AppConfigModel.instance().todos.delete(id_todo_item)
        self._persist()
        return item

    def restore_item(self, item: TodoItemModel) -> ValidationResult:
        """Re-insert a previously deleted TODO item, preserving its identity.

        Used to implement the undo toast of spec §2.5.

        Args:
            item: The item to restore, exactly as it was before deletion.

        Returns:
            A successful ValidationResult once persisted.
        """
        AppConfigModel.instance().todos.create(item)
        self._persist()
        return ValidationResult.ok()

    def delete_list(self, id_pomodoro: str) -> int:
        """Delete every TODO item belonging to `id_pomodoro` (spec §2.5).

        Returns:
            The number of items actually removed.
        """
        removed = AppConfigModel.instance().todos.delete_for_pomodoro(id_pomodoro)
        if removed:
            self._persist()
        return removed

    def _record_state_change(
        self, item: TodoItemModel, old_state: TodoStateEnum, new_state: TodoStateEnum, *, pomodoro_name: str
    ) -> None:
        """Append a TodoHistoryEntryModel for one state transition and purge overflow."""
        entry = TodoHistoryEntryModel(
            id_history_entry=str(uuid.uuid4()),
            id_todo_item=item.id_todo_item,
            id_pomodoro=item.id_pomodoro,
            label_snapshot=item.label,
            pomodoro_name_snapshot=pomodoro_name,
            old_state=old_state,
            new_state=new_state,
            changed_at=datetime.now(UTC),
        )
        history = AppConfigModel.instance().todo_history
        history.create(entry)
        history.purge(MAX_TODO_HISTORY_ENTRIES)
        self._logger.debug("Changement d'état TODO enregistré dans l'historique : id=%s", entry.id_history_entry)

    def _persist(self) -> None:
        """Save the current singleton configuration through the repository."""
        self._config_repository.save(AppConfigModel.instance())


# EOF
