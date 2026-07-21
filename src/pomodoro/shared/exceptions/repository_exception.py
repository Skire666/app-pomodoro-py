"""Project-level exceptions raised by the Repository layer.

Per AGENTS.md §12.3, only Repositories raise these: vendor and stdlib
exceptions (I/O errors, JSON parsing failures, ...) are caught at the
Repository boundary and re-raised as one of the exceptions below.
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from pathlib import Path


class RepositoryError(Exception):
    """Base class for all exceptions raised by a Repository."""


class ConfigReadError(RepositoryError):
    """Raised when `config-pomodoro.json` cannot be read from disk."""

    def __init__(self, config_path: Path) -> None:
        """Build the error message for a failed read of `config_path`."""
        super().__init__(f"Impossible de lire {config_path}")


class ConfigWriteError(RepositoryError):
    """Raised when `config-pomodoro.json` cannot be written to disk."""

    def __init__(self, config_path: Path) -> None:
        """Build the error message for a failed write of `config_path`."""
        super().__init__(f"Impossible d'écrire {config_path}")


class ConfigCorruptedError(RepositoryError):
    """Raised when `config-pomodoro.json` contains invalid JSON."""

    def __init__(self, config_path: Path) -> None:
        """Build the error message for corrupted JSON found in `config_path`."""
        super().__init__(f"Le fichier de configuration est corrompu (JSON invalide) : {config_path}")


# EOF
