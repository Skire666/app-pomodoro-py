"""Contract for the TODO list business-logic service."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from typing import Protocol

from pomodoro.models.todo_item_model import TodoItemModel
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum
from pomodoro.shared.validation_result import ValidationResult


class ITodoService(Protocol):
    """Service contract for a pomodoro's TODO list (spec §2.5, §2.6)."""

    @staticmethod
    def generate_id() -> str:
        """Generate a unique identifier for a new TODO item."""
        ...

    def list_for_pomodoro(self, id_pomodoro: str) -> tuple[TodoItemModel, ...]:
        """List every TODO item belonging to `id_pomodoro`, in storage order."""
        ...

    def count_active_for_pomodoro(self, id_pomodoro: str) -> int:
        """Count non-cancelled TODO items for `id_pomodoro` (spec §2.2 tab label)."""
        ...

    def add_item(self, id_pomodoro: str, label: str) -> ValidationResult:
        """Create and persist a new TODO item (spec §2.5, initial state 'À faire').

        Args:
            id_pomodoro: Identifier of the owning pomodoro.
            label: Text label of the new item.

        Returns:
            A successful ValidationResult once persisted, or a failed one
            if the label is empty.
        """
        ...

    def rename_item(self, id_todo_item: str, label: str) -> ValidationResult:
        """Rename a TODO item in place (spec §2.5 inline edit).

        Args:
            id_todo_item: Identifier of the item to rename.
            label: The new label.

        Returns:
            A successful ValidationResult once persisted, or a failed one
            if the item does not exist or the label is empty.
        """
        ...

    def change_state(self, id_todo_item: str, new_state: TodoStateEnum) -> ValidationResult:
        """Change a TODO item's state and record it in history (spec §2.5, §2.6).

        Args:
            id_todo_item: Identifier of the item to update.
            new_state: The state to transition to.

        Returns:
            A successful ValidationResult once persisted, or a failed one
            if the item does not exist.
        """
        ...

    def duplicate_item(self, id_todo_item: str) -> TodoItemModel | None:
        """Duplicate a TODO item, resetting its state (spec §2.5).

        Args:
            id_todo_item: Identifier of the item to duplicate.

        Returns:
            The newly created copy, or None if `id_todo_item` does not exist.
        """
        ...

    def delete_item(self, id_todo_item: str) -> TodoItemModel | None:
        """Delete a single TODO item (spec §2.5, no confirmation required).

        Returns:
            The removed item, so the caller can offer an undo (spec §2.5
            toast), or None if no item matched `id_todo_item`.
        """
        ...

    def restore_item(self, item: TodoItemModel) -> ValidationResult:
        """Re-insert a previously deleted TODO item, preserving its identity.

        Used to implement the undo toast of spec §2.5.

        Args:
            item: The item to restore, exactly as it was before deletion.

        Returns:
            A successful ValidationResult once persisted.
        """
        ...

    def delete_list(self, id_pomodoro: str) -> int:
        """Delete every TODO item belonging to `id_pomodoro` (spec §2.5).

        Returns:
            The number of items actually removed.
        """
        ...


# EOF
