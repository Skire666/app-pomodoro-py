"""Base contract shared by every error-code enum in the project."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from enum import Enum


class BaseErrorCode(Enum):
    """Base class for all project error-code enums.

    Each member maps an error identifier to its French, user-facing message
    (see AGENTS.md §6 and §12.2). Concrete subclasses declare their own
    members and may override `try_simplify_exception` to map a raw,
    technical exception onto one of their known codes.
    """

    @property
    def message(self) -> str:
        """The French, user-facing message carried by this error code."""
        return str(self.value)

    @staticmethod
    def try_simplify_exception(excp: Exception) -> BaseErrorCode | None:
        """Map a raw exception to a known error code, if possible.

        Args:
            excp: The exception caught by the calling layer.

        Returns:
            A known error code describing `excp`, or None if this enum has
            no mapping for it.
        """
        return None


# EOF
