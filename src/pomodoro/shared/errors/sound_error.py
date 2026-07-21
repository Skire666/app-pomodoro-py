"""Error codes for sound file resolution and playback."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from pomodoro.shared.errors.base_error import BaseErrorCode


class ErrorCodeSound(BaseErrorCode):
    """Error codes covering sound file access and playback (spec §3.4)."""

    SND_1001 = "Son introuvable, lecture silencieuse."
    SND_9999 = "Erreur inconnue."


# EOF
