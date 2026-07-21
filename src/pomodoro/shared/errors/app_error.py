"""Generic, application-wide error codes."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from pomodoro.shared.errors.base_error import BaseErrorCode


class ErrorCodeApp(BaseErrorCode):
    """Fallback error code for failures not tied to a specific feature area."""

    APP_9999 = "Une erreur inattendue est survenue."


# EOF
