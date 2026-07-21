"""Error codes for pomodoro validation and lifecycle guards."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from pomodoro.shared.errors.base_error import BaseErrorCode


class ErrorCodePomodoro(BaseErrorCode):
    """Error codes covering pomodoro validation and lifecycle rules (spec §2.3, §3.4)."""

    POM_1001 = "Le nom est requis."
    POM_1002 = "La durée doit être supérieure à 0."
    POM_1003 = "Arrêtez la session en cours avant de supprimer ce pomodoro."
    POM_9999 = "Erreur inconnue."


# EOF
