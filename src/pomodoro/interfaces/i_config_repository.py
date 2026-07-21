"""Contract for reading and writing `config-pomodoro.json`."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from typing import Protocol

from pomodoro.models.app_config_model import AppConfigModel


class IConfigRepository(Protocol):
    """Repository contract for the application configuration file (AGENTS.md §5, §13.1)."""

    def load(self) -> AppConfigModel:
        """Load the configuration from disk, using the repository's cache when valid.

        Returns:
            The hydrated configuration aggregate.

        Raises:
            ConfigReadError: If the file cannot be read.
            ConfigCorruptedError: If the file contains invalid JSON.
        """
        ...

    def save(self, config: AppConfigModel) -> None:
        """Persist `config` to disk atomically (write to `.tmp`, then rename).

        Args:
            config: The configuration aggregate to persist.

        Raises:
            ConfigWriteError: If the file cannot be written.
        """
        ...

    def invalidate_cache(self) -> None:
        """Force the next `load()` call to re-read the file from disk."""
        ...


# EOF
