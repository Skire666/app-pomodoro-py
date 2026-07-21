"""Sound configuration embedded in a pomodoro definition."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from dataclasses import dataclass
from typing import Any, Final, Self

DEFAULT_SOUND_VOLUME: Final[int] = 80
DEFAULT_SOUND_REPEAT_COUNT: Final[int] = 1
DEFAULT_SOUND_REPEAT_INTERVAL_SECONDS: Final[int] = 10


@dataclass(slots=True)
class SoundSettingsModel:
    """The sound settings of a pomodoro (spec §2.3): file, volume, repeats.

    This is a plain value object with no identity of its own: it is always
    persisted as part of the owning `PomodoroModel` and, unlike a top-level
    entity, does not follow the full Model contract of AGENTS.md §13.2
    (no `id_xxxx`, `copy`, or `clear`).
    """

    path: str | None
    volume: int
    repeat_count: int
    repeat_interval_seconds: int

    @classmethod
    def get_default(cls) -> Self:
        """Build the default sound settings: silent, at 80% volume."""
        return cls(
            path=None,
            volume=DEFAULT_SOUND_VOLUME,
            repeat_count=DEFAULT_SOUND_REPEAT_COUNT,
            repeat_interval_seconds=DEFAULT_SOUND_REPEAT_INTERVAL_SECONDS,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize these sound settings to a JSON-compatible dictionary."""
        return {
            "path": self.path,
            "volume": self.volume,
            "repeat_count": self.repeat_count,
            "repeat_interval_seconds": self.repeat_interval_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild sound settings from a dictionary produced by `to_dict`.

        Args:
            data: A JSON-compatible dictionary as returned by `to_dict`.

        Returns:
            The hydrated sound settings.
        """
        return cls(
            path=data["path"],
            volume=data["volume"],
            repeat_count=data["repeat_count"],
            repeat_interval_seconds=data["repeat_interval_seconds"],
        )


# EOF
