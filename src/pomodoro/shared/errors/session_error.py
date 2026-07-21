"""Error codes for the active pomodoro session."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from pomodoro.shared.errors.base_error import BaseErrorCode


class ErrorCodeSession(BaseErrorCode):
    """Error codes covering the active pomodoro session (spec §2.4)."""

    SES_1001 = "Un pomodoro est déjà en cours d'exécution."
    SES_1002 = "Aucune session active."
    SES_9999 = "Erreur inconnue."


# EOF
