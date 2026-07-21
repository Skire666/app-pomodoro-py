"""Contract for checking sound file availability on disk."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from typing import Protocol


class ISoundRepository(Protocol):
    """Repository contract for sound file lookups (spec §3.4)."""

    def exists(self, sound_path: str) -> bool:
        """Return True if `sound_path` points to a file that exists on disk."""
        ...


# EOF
