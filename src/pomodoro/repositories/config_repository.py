"""Repository reading and writing `config-pomodoro.json` (AGENTS.md §5, §13.1)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import json
import logging
from pathlib import Path

from pomodoro.models.app_config_model import AppConfigModel
from pomodoro.shared.exceptions.repository_exception import ConfigCorruptedError, ConfigReadError, ConfigWriteError


class ConfigRepository:
    """The only class allowed to read or write `config-pomodoro.json`.

    Loads are cached in memory: `load()` re-reads the file from disk only
    after `invalidate_cache()` has been called or before the very first
    call. Writes are atomic: the new content is written to a sibling
    `.tmp` file, then renamed over the target (spec §3.1).
    """

    def __init__(self, config_path: Path) -> None:
        """Initialize the repository for the configuration file at `config_path`."""
        self._config_path = config_path
        self._cache: AppConfigModel | None = None
        self._logger = logging.getLogger(self.__class__.__name__)

    def load(self) -> AppConfigModel:
        """Load the configuration, using the cache when it is already warm.

        Returns:
            The hydrated configuration aggregate.

        Raises:
            ConfigReadError: If the file cannot be read.
            ConfigCorruptedError: If the file contains invalid JSON.
        """
        if self._cache is not None:
            self._logger.debug("Configuration servie depuis le cache : %s", self._config_path)
            return self._cache
        self._cache = self._read_from_disk()
        return self._cache

    def _read_from_disk(self) -> AppConfigModel:
        """Read and parse the configuration file, or return a default one."""
        if not self._config_path.exists():
            self._logger.debug("Fichier de configuration absent, valeurs par défaut : %s", self._config_path)
            return AppConfigModel.get_default()
        data = self._parse_json(self._read_text())
        self._logger.debug("Configuration chargée depuis %s", self._config_path)
        return AppConfigModel.from_dict(data)

    def _read_text(self) -> str:
        """Read the raw file content, wrapping I/O failures."""
        try:
            return self._config_path.read_text(encoding="utf-8")
        except OSError as excp:
            self._logger.debug("Échec de lecture de %s : %s", self._config_path, excp)
            raise ConfigReadError(self._config_path) from excp

    def _parse_json(self, raw_text: str) -> dict[str, object]:
        """Parse `raw_text` as JSON, wrapping decoding failures."""
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError as excp:
            self._logger.debug("Fichier de configuration corrompu : %s", excp)
            raise ConfigCorruptedError(self._config_path) from excp

    def save(self, config: AppConfigModel) -> None:
        """Persist `config` to disk atomically and refresh the cache.

        Args:
            config: The configuration aggregate to persist.

        Raises:
            ConfigWriteError: If the file cannot be written.
        """
        tmp_path = self._config_path.with_name(self._config_path.name + ".tmp")
        payload = json.dumps(config.to_dict(), indent=2, ensure_ascii=False)
        try:
            tmp_path.write_text(payload, encoding="utf-8")
            tmp_path.replace(self._config_path)
        except OSError as excp:
            self._logger.debug("Échec d'écriture de %s : %s", self._config_path, excp)
            raise ConfigWriteError(self._config_path) from excp
        self._cache = config
        self._logger.debug("Configuration enregistrée dans %s", self._config_path)

    def invalidate_cache(self) -> None:
        """Force the next `load()` call to re-read the file from disk."""
        self._cache = None


# EOF
