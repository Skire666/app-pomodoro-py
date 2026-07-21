"""Domain entity representing one completed or interrupted pomodoro session."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from datetime import UTC, datetime
from typing import Any, Self

from pomodoro.shared.enums.copy_mode_enum import CopyModeEnum
from pomodoro.shared.enums.pomodoro_history_status_enum import PomodoroHistoryStatusEnum
from pomodoro.shared.errors.history_error import ErrorCodeHistory
from pomodoro.shared.validation_result import ValidationResult


class PomodoroHistoryEntryModel:
    """A snapshot of one pomodoro session, recorded in history (spec §2.6)."""

    def __init__(
        self,
        id_history_entry: str,
        id_pomodoro: str,
        name_snapshot: str,
        executed_at: datetime,
        planned_duration_seconds: int,
        status: PomodoroHistoryStatusEnum,
    ) -> None:
        """Initialize a history entry from its already-resolved fields."""
        self._id_history_entry = id_history_entry
        self._id_pomodoro = id_pomodoro
        self._name_snapshot = name_snapshot
        self._executed_at = executed_at
        self._planned_duration_seconds = planned_duration_seconds
        self._status = status

    @property
    def id_history_entry(self) -> str:
        """Unique identifier of this history entry."""
        return self._id_history_entry

    @id_history_entry.setter
    def id_history_entry(self, value: str) -> None:
        """Set the unique identifier of this history entry."""
        self._id_history_entry = value

    @property
    def id_pomodoro(self) -> str:
        """Identifier of the source pomodoro (may no longer exist)."""
        return self._id_pomodoro

    @property
    def name_snapshot(self) -> str:
        """Name of the source pomodoro, frozen at execution time."""
        return self._name_snapshot

    @property
    def executed_at(self) -> datetime:
        """Timestamp at which the session started."""
        return self._executed_at

    @property
    def planned_duration_seconds(self) -> int:
        """Duration the session was configured to run, in seconds."""
        return self._planned_duration_seconds

    @property
    def status(self) -> PomodoroHistoryStatusEnum:
        """Outcome of the session: completed or interrupted."""
        return self._status

    @property
    def fieldnames(self) -> tuple[str, ...]:
        """Names of every persisted field, in declaration order."""
        return (
            "id_history_entry",
            "id_pomodoro",
            "name_snapshot",
            "executed_at",
            "planned_duration_seconds",
            "status",
        )

    def validate(self, context: object | None = None) -> ValidationResult:
        """Validate the invariants of a completed history entry.

        Args:
            context: Unused; kept for interface consistency with other models.

        Returns:
            A successful ValidationResult, or a failed one if the status
            was never resolved.
        """
        del context
        if self._status is PomodoroHistoryStatusEnum.E_UNSET:
            return ValidationResult.error(ErrorCodeHistory.HIS_1001, field_name="status")
        return ValidationResult.ok()

    def to_dict(self) -> dict[str, Any]:
        """Serialize this history entry to a JSON-compatible dictionary."""
        return {
            "id_history_entry": self._id_history_entry,
            "id_pomodoro": self._id_pomodoro,
            "name_snapshot": self._name_snapshot,
            "executed_at": self._executed_at.isoformat(),
            "planned_duration_seconds": self._planned_duration_seconds,
            "status": self._status.value,
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
            id_pomodoro=data["id_pomodoro"],
            name_snapshot=data["name_snapshot"],
            executed_at=datetime.fromisoformat(data["executed_at"]),
            planned_duration_seconds=data["planned_duration_seconds"],
            status=PomodoroHistoryStatusEnum(data["status"]),
        )

    @classmethod
    def get_default(cls) -> Self:
        """Build a fully initialized history entry with neutral default values."""
        return cls(
            id_history_entry="",
            id_pomodoro="",
            name_snapshot="",
            executed_at=datetime.now(UTC),
            planned_duration_seconds=0,
            status=PomodoroHistoryStatusEnum.E_UNSET,
        )

    def mark_as_created(self) -> None:
        """Stamp `executed_at` with the current time.

        History entries have no separate modification timestamp: they are
        write-once records (spec §2.6, read-only).
        """
        self._executed_at = datetime.now(UTC)

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
                id_pomodoro=self._id_pomodoro,
                name_snapshot=self._name_snapshot,
                executed_at=datetime.now(UTC),
                planned_duration_seconds=self._planned_duration_seconds,
                status=self._status,
            )
        return self.from_dict(self.to_dict())

    def clear(self) -> None:
        """Reset this instance to its default state, in place."""
        default = self.get_default()
        self._id_history_entry = default.id_history_entry
        self._id_pomodoro = default.id_pomodoro
        self._name_snapshot = default.name_snapshot
        self._executed_at = default.executed_at
        self._planned_duration_seconds = default.planned_duration_seconds
        self._status = default.status


# EOF
