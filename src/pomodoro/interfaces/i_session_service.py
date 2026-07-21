"""Contract for the active pomodoro session business-logic service."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from typing import Protocol

from pomodoro.models.active_session_model import ActiveSessionModel
from pomodoro.shared.validation_result import ValidationResult


class ISessionService(Protocol):
    """Service contract for the single active pomodoro session (spec §2.4)."""

    def get_active(self) -> ActiveSessionModel | None:
        """Return the currently running session, or None if idle."""
        ...

    def start(self, id_pomodoro: str) -> ValidationResult:
        """Start a new session for `id_pomodoro`.

        Args:
            id_pomodoro: Identifier of the pomodoro to start.

        Returns:
            A successful ValidationResult once started, or a failed one if
            another session is already active or the pomodoro is unknown.
        """
        ...

    def pause(self) -> ValidationResult:
        """Pause the currently running session.

        Returns:
            A successful ValidationResult once paused, or a failed one if
            no session is active.
        """
        ...

    def resume(self) -> ValidationResult:
        """Resume the currently paused session.

        Returns:
            A successful ValidationResult once resumed, or a failed one if
            no session is active.
        """
        ...

    def reset(self) -> ValidationResult:
        """Reset the current session's countdown to the full planned duration.

        Returns:
            A successful ValidationResult once reset, or a failed one if
            no session is active.
        """
        ...

    def stop_interrupted(self) -> ValidationResult:
        """Stop the current session early, recording it as interrupted.

        Returns:
            A successful ValidationResult once recorded, or a failed one if
            no session is active.
        """
        ...

    def complete(self) -> ValidationResult:
        """Record the current session as completed, having reached 00:00:00.

        Returns:
            A successful ValidationResult once recorded, or a failed one if
            no session is active.
        """
        ...


# EOF
