"""Domain entity representing one TODO item state change, recorded in history."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from datetime import UTC, datetime
from typing import Any, Self

from pomodoro.shared.enums.copy_mode_enum import CopyModeEnum
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum
from pomodoro.shared.errors.history_error import ErrorCodeHistory
from pomodoro.shared.validation_result import ValidationResult


class TodoHistoryEntryModel:
    """A snapshot of one TODO item state change (spec §2.6, one row per change)."""

    def __init__(
        self,
        id_history_entry: str,
        id_todo_item: str,
        id_pomodoro: str,
        label_snapshot: str,
        pomodoro_name_snapshot: str,
        old_state: TodoStateEnum,
        new_state: TodoStateEnum,
        changed_at: datetime,
    ) -> None:
        """Initialize a history entry from its already-resolved fields."""
        self._id_history_entry = id_history_entry
        self._id_todo_item = id_todo_item
        self._id_pomodoro = id_pomodoro
        self._label_snapshot = label_snapshot
        self._pomodoro_name_snapshot = pomodoro_name_snapshot
        self._old_state = old_state
        self._new_state = new_state
        self._changed_at = changed_at

    @property
    def id_history_entry(self) -> str:
        """Unique identifier of this history entry."""
        return self._id_history_entry

    @id_history_entry.setter
    def id_history_entry(self, value: str) -> None:
        """Set the unique identifier of this history entry."""
        self._id_history_entry = value

    @property
    def id_todo_item(self) -> str:
        """Identifier of the source TODO item."""
        return self._id_todo_item

    @property
    def id_pomodoro(self) -> str:
        """Identifier of the pomodoro the TODO item belongs to."""
        return self._id_pomodoro

    @property
    def label_snapshot(self) -> str:
        """Label of the TODO item, frozen at the time of the change."""
        return self._label_snapshot

    @property
    def pomodoro_name_snapshot(self) -> str:
        """Name of the associated pomodoro, frozen at the time of the change."""
        return self._pomodoro_name_snapshot

    @property
    def old_state(self) -> TodoStateEnum:
        """State the TODO item transitioned from."""
        return self._old_state

    @property
    def new_state(self) -> TodoStateEnum:
        """State the TODO item transitioned to."""
        return self._new_state

    @property
    def changed_at(self) -> datetime:
        """Timestamp at which the state change occurred."""
        return self._changed_at

    @property
    def fieldnames(self) -> tuple[str, ...]:
        """Names of every persisted field, in declaration order."""
        return (
            "id_history_entry",
            "id_todo_item",
            "id_pomodoro",
            "label_snapshot",
            "pomodoro_name_snapshot",
            "old_state",
            "new_state",
            "changed_at",
        )

    def validate(self, context: object | None = None) -> ValidationResult:
        """Validate the invariants of a TODO history entry.

        Args:
            context: Unused; kept for interface consistency with other models.

        Returns:
            A successful ValidationResult, or a failed one if either state
            was never resolved.
        """
        del context
        if self._old_state is TodoStateEnum.E_UNSET or self._new_state is TodoStateEnum.E_UNSET:
            return ValidationResult.error(ErrorCodeHistory.HIS_1002, field_name="new_state")
        return ValidationResult.ok()

    def to_dict(self) -> dict[str, Any]:
        """Serialize this history entry to a JSON-compatible dictionary."""
        return {
            "id_history_entry": self._id_history_entry,
            "id_todo_item": self._id_todo_item,
            "id_pomodoro": self._id_pomodoro,
            "label_snapshot": self._label_snapshot,
            "pomodoro_name_snapshot": self._pomodoro_name_snapshot,
            "old_state": self._old_state.value,
            "new_state": self._new_state.value,
            "changed_at": self._changed_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a history entry from a dictionary produced by `to_dict`.

        Args:
            data: A JSON-compatible dictionary as returned by `to_dict`.

        Returns:
            The hydrated history entry.
        """
        return cls(
            id_history_entry=data["id_history_entry"],
            id_todo_item=data["id_todo_item"],
            id_pomodoro=data["id_pomodoro"],
            label_snapshot=data["label_snapshot"],
            pomodoro_name_snapshot=data["pomodoro_name_snapshot"],
            old_state=TodoStateEnum(data["old_state"]),
            new_state=TodoStateEnum(data["new_state"]),
            changed_at=datetime.fromisoformat(data["changed_at"]),
        )

    @classmethod
    def get_default(cls) -> Self:
        """Build a fully initialized history entry with neutral default values."""
        return cls(
            id_history_entry="",
            id_todo_item="",
            id_pomodoro="",
            label_snapshot="",
            pomodoro_name_snapshot="",
            old_state=TodoStateEnum.E_UNSET,
            new_state=TodoStateEnum.E_UNSET,
            changed_at=datetime.now(UTC),
        )

    def mark_as_created(self) -> None:
        """Stamp `changed_at` with the current time.

        History entries have no separate modification timestamp: they are
        write-once records (spec §2.6, read-only).
        """
        self._changed_at = datetime.now(UTC)

    def mark_as_modified(self) -> None:
        """No-op: history entries are immutable once recorded (spec §2.6)."""

    def copy(self, mode: CopyModeEnum) -> Self:
        """Copy this history entry.

        Args:
            mode: `E_TECHNICAL` for an identical clone (same identity);
                `E_BUSINESS` for a functional copy without an identity.

        Returns:
            The copied history entry.
        """
        if mode is CopyModeEnum.E_BUSINESS:
            return type(self)(
                id_history_entry="",
                id_todo_item=self._id_todo_item,
                id_pomodoro=self._id_pomodoro,
                label_snapshot=self._label_snapshot,
                pomodoro_name_snapshot=self._pomodoro_name_snapshot,
                old_state=self._old_state,
                new_state=self._new_state,
                changed_at=datetime.now(UTC),
            )
        return self.from_dict(self.to_dict())

    def clear(self) -> None:
        """Reset this instance to its default state, in place."""
        default = self.get_default()
        self._id_history_entry = default.id_history_entry
        self._id_todo_item = default.id_todo_item
        self._id_pomodoro = default.id_pomodoro
        self._label_snapshot = default.label_snapshot
        self._pomodoro_name_snapshot = default.pomodoro_name_snapshot
        self._old_state = default.old_state
        self._new_state = default.new_state
        self._changed_at = default.changed_at


# EOF
