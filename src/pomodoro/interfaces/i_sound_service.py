"""Contract for the sound availability business-logic service."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from typing import Protocol

from pomodoro.shared.validation_result import ValidationResult


class ISoundService(Protocol):
    """Service contract wrapping sound file availability checks (spec §3.4)."""

    def check_available(self, sound_path: str | None) -> ValidationResult:
        """Check whether `sound_path` can be played.

        Args:
            sound_path: Path to the configured sound file, or None if the
                pomodoro is silent.

        Returns:
            A successful ValidationResult if `sound_path` is None (silent
            by design) or points to an existing file; a failed one
            carrying `ErrorCodeSound.SND_1001` otherwise.
        """
        ...


# EOF
