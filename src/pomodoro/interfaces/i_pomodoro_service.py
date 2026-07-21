"""Contract for the pomodoro business-logic service."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from typing import Protocol

from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.shared.enums.pomodoro_sort_mode_enum import PomodoroSortModeEnum
from pomodoro.shared.validation_result import ValidationResult


class IPomodoroService(Protocol):
    """Service contract for pomodoro definitions (spec §2.1, §2.3, §3.4)."""

    @staticmethod
    def generate_id() -> str:
        """Generate a unique identifier for a new pomodoro."""
        ...

    def list_all(
        self,
        name_filter: str = "",
        sort_mode: PomodoroSortModeEnum = PomodoroSortModeEnum.E_UNSET,
    ) -> tuple[PomodoroModel, ...]:
        """List pomodoros filtered and sorted per the list screen rules (spec §2.1).

        Args:
            name_filter: Case-insensitive substring to match against names.
            sort_mode: The sort criterion to apply.

        Returns:
            The filtered and sorted pomodoros.
        """
        ...

    def get(self, id_pomodoro: str) -> PomodoroModel | None:
        """Return the pomodoro matching `id_pomodoro`, or None if absent."""
        ...

    def save(self, pomodoro: PomodoroModel) -> ValidationResult:
        """Validate and persist `pomodoro`, creating or updating it.

        Args:
            pomodoro: The pomodoro to validate and persist.

        Returns:
            A successful ValidationResult once persisted, or the failed
            result explaining why it was rejected.
        """
        ...

    def duplicate(self, id_pomodoro: str) -> PomodoroModel | None:
        """Duplicate a pomodoro with a freshly generated identity (spec §2.1).

        Args:
            id_pomodoro: Identifier of the pomodoro to duplicate.

        Returns:
            The newly created copy, or None if `id_pomodoro` does not exist.
        """
        ...

    def delete(self, id_pomodoro: str, *, has_active_session: bool) -> ValidationResult:
        """Delete a pomodoro and its associated TODO items (spec §3.4).

        Args:
            id_pomodoro: Identifier of the pomodoro to delete.
            has_active_session: True if a session is currently running on
                this pomodoro; deletion is then blocked.

        Returns:
            A successful ValidationResult once deleted, or a failed one if
            deletion is blocked by an active session.
        """
        ...


# EOF
