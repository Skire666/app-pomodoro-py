"""Domain entity representing a single TODO item attached to a pomodoro."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from datetime import UTC, datetime
from typing import Any, Self

from pomodoro.shared.enums.copy_mode_enum import CopyModeEnum
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum
from pomodoro.shared.errors.todo_error import ErrorCodeTodo
from pomodoro.shared.validation_result import ValidationResult


class TodoItemModel:
    """A single TODO line belonging to a pomodoro's TODO list (spec §2.5)."""

    def __init__(
        self,
        id_todo_item: str,
        id_pomodoro: str,
        label: str,
        state: TodoStateEnum,
        created_at: datetime,
        modified_at: datetime,
    ) -> None:
        """Initialize a TODO item from its already-resolved fields."""
        self._id_todo_item = id_todo_item
        self._id_pomodoro = id_pomodoro
        self._label = label
        self._state = state
        self._created_at = created_at
        self._modified_at = modified_at

    @property
    def id_todo_item(self) -> str:
        """Unique identifier of this TODO item."""
        return self._id_todo_item

    @id_todo_item.setter
    def id_todo_item(self, value: str) -> None:
        """Set the unique identifier of this TODO item."""
        self._id_todo_item = value

    @property
    def id_pomodoro(self) -> str:
        """Identifier of the pomodoro this TODO item belongs to."""
        return self._id_pomodoro

    @id_pomodoro.setter
    def id_pomodoro(self, value: str) -> None:
        """Set the identifier of the pomodoro this TODO item belongs to."""
        self._id_pomodoro = value

    @property
    def label(self) -> str:
        """Text label of the TODO item."""
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        """Set the text label of the TODO item."""
        self._label = value

    @property
    def state(self) -> TodoStateEnum:
        """Current lifecycle state of the TODO item."""
        return self._state

    @state.setter
    def state(self, value: TodoStateEnum) -> None:
        """Set the current lifecycle state of the TODO item."""
        self._state = value

    @property
    def created_at(self) -> datetime:
        """Timestamp at which the TODO item was created."""
        return self._created_at

    @property
    def modified_at(self) -> datetime:
        """Timestamp at which the TODO item was last modified."""
        return self._modified_at

    @property
    def fieldnames(self) -> tuple[str, ...]:
        """Names of every persisted field, in declaration order."""
        return ("id_todo_item", "id_pomodoro", "label", "state", "created_at", "modified_at")

    def validate(self, context: object | None = None) -> ValidationResult:
        """Validate the TODO item against the business rules of spec §2.5.

        Args:
            context: Unused; kept for interface consistency with other models.

        Returns:
            A successful ValidationResult, or a failed one if the label is
            empty.
        """
        del context
        if not self._label.strip():
            return ValidationResult.error(ErrorCodeTodo.TDI_1001, field_name="label")
        return ValidationResult.ok()

    def to_dict(self) -> dict[str, Any]:
        """Serialize this TODO item to a JSON-compatible dictionary."""
        return {
            "id_todo_item": self._id_todo_item,
            "id_pomodoro": self._id_pomodoro,
            "label": self._label,
            "state": self._state.value,
            "created_at": self._created_at.isoformat(),
            "modified_at": self._modified_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a TODO item from a dictionary produced by `to_dict`.

        Args:
            data: A JSON-compatible dictionary as returned by `to_dict`.

        Returns:
            The hydrated TODO item.
        """
        return cls(
            id_todo_item=data["id_todo_item"],
            id_pomodoro=data["id_pomodoro"],
            label=data["label"],
            state=TodoStateEnum(data["state"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
        )

    @classmethod
    def get_default(cls) -> Self:
        """Build a fully initialized TODO item with sensible default values."""
        now = datetime.now(UTC)
        return cls(
            id_todo_item="",
            id_pomodoro="",
            label="",
            state=TodoStateEnum.E_TODO,
            created_at=now,
            modified_at=now,
        )

    def mark_as_created(self) -> None:
        """Stamp `created_at` and `modified_at` with the current time."""
        now = datetime.now(UTC)
        self._created_at = now
        self._modified_at = now

    def mark_as_modified(self) -> None:
        """Stamp `modified_at` with the current time."""
        self._modified_at = datetime.now(UTC)

    def copy(self, mode: CopyModeEnum) -> Self:
        """Copy this TODO item.

        Args:
            mode: `E_TECHNICAL` for an identical clone (same identity and
                timestamps); `E_BUSINESS` for a functional copy without an
                identity, ready for a new `id_todo_item` to be assigned.

        Returns:
            The copied TODO item.
        """
        if mode is CopyModeEnum.E_BUSINESS:
            clone = self.get_default()
            clone.id_pomodoro = self._id_pomodoro
            clone.label = self._label
            clone.state = self._state
            return clone
        return self.from_dict(self.to_dict())

    def clear(self) -> None:
        """Reset this instance to its default state, in place."""
        default = self.get_default()
        self._id_todo_item = default.id_todo_item
        self._id_pomodoro = default.id_pomodoro
        self._label = default.label
        self._state = default.state
        self._created_at = default.created_at
        self._modified_at = default.modified_at


# EOF
