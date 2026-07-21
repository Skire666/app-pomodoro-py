"""Repository checking sound file availability on disk (AGENTS.md §13.1)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
from pathlib import Path


class SoundRepository:
    """The only class allowed to touch the filesystem for sound file lookups."""

    def __init__(self) -> None:
        """Initialize the repository."""
        self._logger = logging.getLogger(self.__class__.__name__)

    def exists(self, sound_path: str) -> bool:
        """Return True if `sound_path` points to a file that exists on disk."""
        found = Path(sound_path).is_file()
        if not found:
            self._logger.debug("Fichier son introuvable : %s", sound_path)
        return found


# EOF
