"""Error codes for reading and writing the application configuration file."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from pomodoro.shared.errors.base_error import BaseErrorCode
from pomodoro.shared.exceptions.repository_exception import ConfigCorruptedError, ConfigReadError, ConfigWriteError


class ErrorCodeConfig(BaseErrorCode):
    """Error codes covering `config-pomodoro.json` access failures."""

    CFG_1001 = "Impossible de lire le fichier de configuration."
    CFG_1002 = "Impossible d'écrire le fichier de configuration."
    CFG_1003 = "Le fichier de configuration est corrompu (JSON invalide)."
    CFG_9999 = "Erreur inconnue."

    @staticmethod
    def try_simplify_exception(excp: Exception) -> ErrorCodeConfig | None:
        """Map a repository exception to a known configuration error code.

        Args:
            excp: The exception caught by the calling Service.

        Returns:
            A known error code, or None if `excp` is not recognized.
        """
        if isinstance(excp, ConfigCorruptedError):
            return ErrorCodeConfig.CFG_1003
        if isinstance(excp, ConfigReadError):
            return ErrorCodeConfig.CFG_1001
        if isinstance(excp, ConfigWriteError):
            return ErrorCodeConfig.CFG_1002
        return None


# EOF
