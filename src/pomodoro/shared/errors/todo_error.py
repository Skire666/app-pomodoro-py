"""Error codes for TODO item validation."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from pomodoro.shared.errors.base_error import BaseErrorCode


class ErrorCodeTodo(BaseErrorCode):
    """Error codes covering TODO item validation (spec §2.5)."""

    TDI_1001 = "Le libellé est requis."
    TDI_9999 = "Erreur inconnue."


# EOF
