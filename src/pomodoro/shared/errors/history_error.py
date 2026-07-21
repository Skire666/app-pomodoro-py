"""Error codes for pomodoro and TODO history entries."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from pomodoro.shared.errors.base_error import BaseErrorCode


class ErrorCodeHistory(BaseErrorCode):
    """Error codes covering history entry invariants (spec §2.6)."""

    HIS_1001 = "Le statut de l'entrée d'historique est invalide."
    HIS_1002 = "L'état de l'entrée d'historique TODO est invalide."
    HIS_9999 = "Erreur inconnue."


# EOF
