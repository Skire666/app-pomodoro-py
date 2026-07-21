"""Business logic wrapping sound file availability checks (spec §3.4)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging

from pomodoro.interfaces.i_sound_repository import ISoundRepository
from pomodoro.shared.errors.sound_error import ErrorCodeSound
from pomodoro.shared.validation_result import ValidationResult


class SoundService:
    """Business rules for sound file availability."""

    def __init__(self, sound_repository: ISoundRepository) -> None:
        """Initialize the service with its injected repository."""
        self._sound_repository = sound_repository
        self._logger = logging.getLogger(self.__class__.__name__)

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
        if sound_path is None:
            return ValidationResult.ok()
        if self._sound_repository.exists(sound_path):
            return ValidationResult.ok()
        self._logger.debug("Fichier son indisponible pour la lecture : %s", sound_path)
        return ValidationResult.error(ErrorCodeSound.SND_1001)


# EOF
