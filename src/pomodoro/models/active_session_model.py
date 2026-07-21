"""Domain entity representing the currently running pomodoro session (spec §2.4)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from datetime import UTC, datetime
from typing import Any, Self

from pomodoro.shared.enums.copy_mode_enum import CopyModeEnum
from pomodoro.shared.validation_result import ValidationResult


class ActiveSessionModel:
    """The single, currently running pomodoro session, if any (spec §2.4).

    Persisted as part of `AppConfigModel` so that an interrupted session
    can be offered for resumption after an unexpected shutdown (spec §3.4).
    Identified by `id_pomodoro` since at most one session can be active at
    a time. Mutated only through `pause`/`resume`: the underlying fields
    have no public setters, to keep the pause/resume invariants intact.
    """

    def __init__(
        self,
        id_pomodoro: str,
        name_snapshot: str,
        planned_duration_seconds: int,
        accumulated_seconds: int,
        is_paused: bool,
        last_resumed_at: datetime,
        created_at: datetime,
        modified_at: datetime,
    ) -> None:
        """Initialize a session from its already-resolved fields."""
        self._id_pomodoro = id_pomodoro
        self._name_snapshot = name_snapshot
        self._planned_duration_seconds = planned_duration_seconds
        self._accumulated_seconds = accumulated_seconds
        self._is_paused = is_paused
        self._last_resumed_at = last_resumed_at
        self._created_at = created_at
        self._modified_at = modified_at

    @property
    def id_pomodoro(self) -> str:
        """Identifier of the pomodoro this session was started from."""
        return self._id_pomodoro

    @property
    def name_snapshot(self) -> str:
        """Name of the pomodoro, frozen at the time the session started."""
        return self._name_snapshot

    @property
    def planned_duration_seconds(self) -> int:
        """Duration this session was configured to run, in seconds."""
        return self._planned_duration_seconds

    @property
    def accumulated_seconds(self) -> int:
        """Total time elapsed while actively running (excludes paused time)."""
        return self._accumulated_seconds

    @property
    def is_paused(self) -> bool:
        """True while the countdown is frozen (spec §2.4 'Pause')."""
        return self._is_paused

    @property
    def last_resumed_at(self) -> datetime:
        """Timestamp at which the countdown was last started or resumed."""
        return self._last_resumed_at

    @property
    def created_at(self) -> datetime:
        """Timestamp at which the session was created."""
        return self._created_at

    @property
    def modified_at(self) -> datetime:
        """Timestamp at which the session was last modified."""
        return self._modified_at

    @property
    def fieldnames(self) -> tuple[str, ...]:
        """Names of every persisted field, in declaration order."""
        return (
            "id_pomodoro",
            "name_snapshot",
            "planned_duration_seconds",
            "accumulated_seconds",
            "is_paused",
            "last_resumed_at",
            "created_at",
            "modified_at",
        )

    def elapsed_seconds(self, now: datetime) -> int:
        """Return the total elapsed running time as of `now`.

        Args:
            now: The current time, injected for deterministic testing.

        Returns:
            The elapsed seconds, including running time since the last resume.
        """
        if self._is_paused:
            return self._accumulated_seconds
        return self._accumulated_seconds + int((now - self._last_resumed_at).total_seconds())

    def remaining_seconds(self, now: datetime) -> int:
        """Return the remaining countdown time as of `now`, floored at zero.

        Args:
            now: The current time, injected for deterministic testing.

        Returns:
            The remaining seconds before this session completes.
        """
        return max(0, self._planned_duration_seconds - self.elapsed_seconds(now))

    def is_complete(self, now: datetime) -> bool:
        """Return True if this session has reached its planned duration."""
        return self.remaining_seconds(now) <= 0

    def pause(self, now: datetime) -> None:
        """Freeze the countdown, accumulating elapsed time (spec §2.4 'Pause').

        Args:
            now: The current time, injected for deterministic testing.
        """
        if self._is_paused:
            return
        self._accumulated_seconds += int((now - self._last_resumed_at).total_seconds())
        self._is_paused = True
        self._modified_at = now

    def resume(self, now: datetime) -> None:
        """Restart the countdown from where it was paused (spec §2.4 'Reprendre').

        Args:
            now: The current time, injected for deterministic testing.
        """
        if not self._is_paused:
            return
        self._last_resumed_at = now
        self._is_paused = False
        self._modified_at = now

    def reset(self, now: datetime) -> None:
        """Reset the countdown to the full planned duration (spec §2.4 'Reset').

        Running sessions keep running (ticking down again from the full
        duration); paused sessions stay paused, ready to resume at the
        full duration.

        Args:
            now: The current time, injected for deterministic testing.
        """
        self._accumulated_seconds = 0
        if not self._is_paused:
            self._last_resumed_at = now
        self._modified_at = now

    def validate(self, context: object | None = None) -> ValidationResult:
        """Validate this session's invariants.

        Args:
            context: Unused; kept for interface consistency with other models.

        Returns:
            Always a successful ValidationResult: a session is only ever
            created internally by `SessionService` from already-valid data.
        """
        del context
        return ValidationResult.ok()

    def to_dict(self) -> dict[str, Any]:
        """Serialize this session to a JSON-compatible dictionary."""
        return {
            "id_pomodoro": self._id_pomodoro,
            "name_snapshot": self._name_snapshot,
            "planned_duration_seconds": self._planned_duration_seconds,
            "accumulated_seconds": self._accumulated_seconds,
            "is_paused": self._is_paused,
            "last_resumed_at": self._last_resumed_at.isoformat(),
            "created_at": self._created_at.isoformat(),
            "modified_at": self._modified_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a session from a dictionary produced by `to_dict`.

        Args:
            data: A JSON-compatible dictionary as returned by `to_dict`.

        Returns:
            The hydrated session.
        """
        return cls(
            id_pomodoro=data["id_pomodoro"],
            name_snapshot=data["name_snapshot"],
            planned_duration_seconds=data["planned_duration_seconds"],
            accumulated_seconds=data["accumulated_seconds"],
            is_paused=data["is_paused"],
            last_resumed_at=datetime.fromisoformat(data["last_resumed_at"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
        )

    @classmethod
    def get_default(cls) -> Self:
        """Build a fully initialized, neutral session (not itself a real session)."""
        now = datetime.now(UTC)
        return cls(
            id_pomodoro="",
            name_snapshot="",
            planned_duration_seconds=0,
            accumulated_seconds=0,
            is_paused=True,
            last_resumed_at=now,
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
        """Copy this session.

        Args:
            mode: `E_TECHNICAL` for an identical clone; `E_BUSINESS` for a
                functional copy restarting the countdown from now.

        Returns:
            The copied session.
        """
        if mode is CopyModeEnum.E_BUSINESS:
            now = datetime.now(UTC)
            return type(self)(
                id_pomodoro=self._id_pomodoro,
                name_snapshot=self._name_snapshot,
                planned_duration_seconds=self._planned_duration_seconds,
                accumulated_seconds=0,
                is_paused=False,
                last_resumed_at=now,
                created_at=now,
                modified_at=now,
            )
        return self.from_dict(self.to_dict())

    def clear(self) -> None:
        """Reset this instance to its neutral default state, in place."""
        default = self.get_default()
        self._id_pomodoro = default.id_pomodoro
        self._name_snapshot = default.name_snapshot
        self._planned_duration_seconds = default.planned_duration_seconds
        self._accumulated_seconds = default.accumulated_seconds
        self._is_paused = default.is_paused
        self._last_resumed_at = default.last_resumed_at
        self._created_at = default.created_at
        self._modified_at = default.modified_at


# EOF
