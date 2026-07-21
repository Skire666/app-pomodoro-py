"""Business logic for creating, editing, and removing pomodoros (spec §2.1, §2.3, §3.4)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import uuid

from pomodoro.interfaces.i_config_repository import IConfigRepository
from pomodoro.models.app_config_model import AppConfigModel
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.shared.enums.copy_mode_enum import CopyModeEnum
from pomodoro.shared.enums.pomodoro_sort_mode_enum import PomodoroSortModeEnum
from pomodoro.shared.validation_result import ValidationResult


class PomodoroService:
    """Business rules for pomodoro definitions."""

    def __init__(self, config_repository: IConfigRepository) -> None:
        """Initialize the service with its injected repository."""
        self._config_repository = config_repository
        self._logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def generate_id() -> str:
        """Generate a unique identifier for a new pomodoro."""
        return str(uuid.uuid4())

    def list_all(
        self, name_filter: str = "", sort_mode: PomodoroSortModeEnum = PomodoroSortModeEnum.E_UNSET
    ) -> tuple[PomodoroModel, ...]:
        """List pomodoros filtered and sorted per the list screen rules (spec §2.1)."""
        return AppConfigModel.instance().pomodoros.search(name_filter, sort_mode)

    def get(self, id_pomodoro: str) -> PomodoroModel | None:
        """Return the pomodoro matching `id_pomodoro`, or None if absent."""
        return AppConfigModel.instance().pomodoros.read(id_pomodoro)

    def save(self, pomodoro: PomodoroModel) -> ValidationResult:
        """Validate and persist `pomodoro`, creating or updating it.

        A pomodoro that fails validation is never inserted into the
        collection (spec §2.3: creation is deferred until the name is
        valid).

        Args:
            pomodoro: The pomodoro to validate and persist.

        Returns:
            A successful ValidationResult once persisted, or the failed
            result explaining why it was rejected.
        """
        result = pomodoro.validate()
        if not result.is_valid:
            return result
        collection = AppConfigModel.instance().pomodoros
        if collection.read(pomodoro.id_pomodoro) is None:
            pomodoro.mark_as_created()
            collection.create(pomodoro)
        else:
            pomodoro.mark_as_modified()
            collection.update(pomodoro)
        self._persist()
        self._logger.debug("Pomodoro enregistré : id=%s", pomodoro.id_pomodoro)
        return ValidationResult.ok()

    def duplicate(self, id_pomodoro: str) -> PomodoroModel | None:
        """Duplicate a pomodoro with a freshly generated identity (spec §2.1).

        Args:
            id_pomodoro: Identifier of the pomodoro to duplicate.

        Returns:
            The newly created copy, or None if `id_pomodoro` does not exist.
        """
        source = self.get(id_pomodoro)
        if source is None:
            return None
        clone = source.copy(CopyModeEnum.E_BUSINESS)
        clone.id_pomodoro = self.generate_id()
        clone.mark_as_created()
        AppConfigModel.instance().pomodoros.create(clone)
        self._persist()
        return clone

    def delete(self, id_pomodoro: str) -> ValidationResult:
        """Delete a pomodoro and its associated TODO items (spec §3.4).

        Deletion is always allowed, regardless of whether a session is
        currently running, paused, or stopped for this pomodoro: an active
        session keeps running off its own frozen snapshot and does not
        depend on the pomodoro definition still existing.

        Args:
            id_pomodoro: Identifier of the pomodoro to delete.

        Returns:
            A successful ValidationResult once deleted.
        """
        config = AppConfigModel.instance()
        config.todos.delete_for_pomodoro(id_pomodoro)
        config.pomodoros.delete(id_pomodoro)
        self._persist()
        return ValidationResult.ok()

    def _persist(self) -> None:
        """Save the current singleton configuration through the repository."""
        self._config_repository.save(AppConfigModel.instance())


# EOF
