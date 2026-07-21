"""Domain entity representing a single pomodoro definition."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from datetime import UTC, datetime
from typing import Any, Final, Self

from pomodoro.models.sound_settings_model import SoundSettingsModel
from pomodoro.shared.enums.copy_mode_enum import CopyModeEnum
from pomodoro.shared.errors.pomodoro_error import ErrorCodePomodoro
from pomodoro.shared.validation_result import ValidationResult

DEFAULT_DURATION_SECONDS: Final[int] = 25 * 60


class PomodoroModel:
    """A pomodoro definition: name, duration, and associated sound settings."""

    def __init__(
        self,
        id_pomodoro: str,
        name: str,
        duration_seconds: int,
        sound: SoundSettingsModel,
        created_at: datetime,
        modified_at: datetime,
        last_used_at: datetime | None,
    ) -> None:
        """Initialize a pomodoro from its already-resolved fields."""
        self._id_pomodoro = id_pomodoro
        self._name = name
        self._duration_seconds = duration_seconds
        self._sound = sound
        self._created_at = created_at
        self._modified_at = modified_at
        self._last_used_at = last_used_at

    @property
    def id_pomodoro(self) -> str:
        """Unique identifier of this pomodoro."""
        return self._id_pomodoro

    @id_pomodoro.setter
    def id_pomodoro(self, value: str) -> None:
        """Set the unique identifier of this pomodoro."""
        self._id_pomodoro = value

    @property
    def name(self) -> str:
        """Display name of the pomodoro."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the display name of the pomodoro."""
        self._name = value

    @property
    def duration_seconds(self) -> int:
        """Total configured duration, in seconds."""
        return self._duration_seconds

    @duration_seconds.setter
    def duration_seconds(self, value: int) -> None:
        """Set the total configured duration, in seconds."""
        self._duration_seconds = value

    @property
    def sound(self) -> SoundSettingsModel:
        """Sound settings associated with this pomodoro."""
        return self._sound

    @sound.setter
    def sound(self, value: SoundSettingsModel) -> None:
        """Set the sound settings associated with this pomodoro."""
        self._sound = value

    @property
    def sound_path(self) -> str | None:
        """Path to the configured sound file, or None if silent."""
        return self._sound.path

    @sound_path.setter
    def sound_path(self, value: str | None) -> None:
        """Set the path to the configured sound file."""
        self._sound.path = value

    @property
    def sound_volume(self) -> int:
        """Playback volume of the sound, from 0 to 100."""
        return self._sound.volume

    @sound_volume.setter
    def sound_volume(self, value: int) -> None:
        """Set the playback volume of the sound, from 0 to 100."""
        self._sound.volume = value

    @property
    def sound_repeat_count(self) -> int:
        """Number of times the sound repeats when the pomodoro ends."""
        return self._sound.repeat_count

    @sound_repeat_count.setter
    def sound_repeat_count(self, value: int) -> None:
        """Set the number of times the sound repeats when the pomodoro ends."""
        self._sound.repeat_count = value

    @property
    def sound_repeat_interval_seconds(self) -> int:
        """Delay, in seconds, between two sound repetitions."""
        return self._sound.repeat_interval_seconds

    @sound_repeat_interval_seconds.setter
    def sound_repeat_interval_seconds(self, value: int) -> None:
        """Set the delay, in seconds, between two sound repetitions."""
        self._sound.repeat_interval_seconds = value

    @property
    def created_at(self) -> datetime:
        """Timestamp at which the pomodoro was created."""
        return self._created_at

    @property
    def modified_at(self) -> datetime:
        """Timestamp at which the pomodoro was last modified."""
        return self._modified_at

    @property
    def last_used_at(self) -> datetime | None:
        """Timestamp of the last session started with this pomodoro, if any."""
        return self._last_used_at

    @last_used_at.setter
    def last_used_at(self, value: datetime | None) -> None:
        """Set the timestamp of the last session started with this pomodoro."""
        self._last_used_at = value

    @property
    def fieldnames(self) -> tuple[str, ...]:
        """Names of every persisted field, in declaration order."""
        return (
            "id_pomodoro",
            "name",
            "duration_seconds",
            "sound",
            "created_at",
            "modified_at",
            "last_used_at",
        )

    def validate(self, context: object | None = None) -> ValidationResult:
        """Validate the pomodoro against the business rules of spec §2.3.

        Args:
            context: Unused; kept for interface consistency with other models.

        Returns:
            A successful ValidationResult, or a failed one carrying the
            first violated rule (name required, then duration required).
        """
        del context
        if not self._name.strip():
            return ValidationResult.error(ErrorCodePomodoro.POM_1001, field_name="name")
        if self._duration_seconds <= 0:
            return ValidationResult.error(ErrorCodePomodoro.POM_1002, field_name="duration_seconds")
        return ValidationResult.ok()

    def to_dict(self) -> dict[str, Any]:
        """Serialize this pomodoro to a JSON-compatible dictionary."""
        return {
            "id_pomodoro": self._id_pomodoro,
            "name": self._name,
            "duration_seconds": self._duration_seconds,
            "sound": self._sound.to_dict(),
            "created_at": self._created_at.isoformat(),
            "modified_at": self._modified_at.isoformat(),
            "last_used_at": self._last_used_at.isoformat() if self._last_used_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild a pomodoro from a dictionary produced by `to_dict`.

        Args:
            data: A JSON-compatible dictionary as returned by `to_dict`.

        Returns:
            The hydrated pomodoro.
        """
        last_used_raw = data["last_used_at"]
        return cls(
            id_pomodoro=data["id_pomodoro"],
            name=data["name"],
            duration_seconds=data["duration_seconds"],
            sound=SoundSettingsModel.from_dict(data["sound"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
            last_used_at=datetime.fromisoformat(last_used_raw) if last_used_raw else None,
        )

    @classmethod
    def get_default(cls) -> Self:
        """Build a fully initialized pomodoro with sensible default values."""
        now = datetime.now(UTC)
        return cls(
            id_pomodoro="",
            name="",
            duration_seconds=DEFAULT_DURATION_SECONDS,
            sound=SoundSettingsModel.get_default(),
            created_at=now,
            modified_at=now,
            last_used_at=None,
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
        """Copy this pomodoro.

        Args:
            mode: `E_TECHNICAL` for an identical clone (same identity and
                timestamps); `E_BUSINESS` for a functional copy without an
                identity, ready for a new `id_pomodoro` to be assigned.

        Returns:
            The copied pomodoro.
        """
        if mode is CopyModeEnum.E_BUSINESS:
            clone = self.get_default()
            clone.name = self._name
            clone.duration_seconds = self._duration_seconds
            clone.sound = SoundSettingsModel.from_dict(self._sound.to_dict())
            return clone
        return self.from_dict(self.to_dict())

    def clear(self) -> None:
        """Reset this instance to its default state, in place."""
        default = self.get_default()
        self._id_pomodoro = default.id_pomodoro
        self._name = default.name
        self._duration_seconds = default.duration_seconds
        self._sound = default.sound
        self._created_at = default.created_at
        self._modified_at = default.modified_at
        self._last_used_at = default.last_used_at


# EOF
