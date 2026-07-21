"""Outcome of a business validation, carrying an optional error code."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from dataclasses import dataclass
from typing import Self

from pomodoro.shared.errors.base_error import BaseErrorCode


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Represents the outcome of validating a model or a business operation.

    Expected failures (invalid input, missing entity, business rule
    violation) are reported through this type rather than raised as
    exceptions (see AGENTS.md §12.2).
    """

    is_valid: bool
    error_code: BaseErrorCode | None = None
    field_name: str | None = None

    @classmethod
    def ok(cls) -> Self:
        """Build a successful validation result."""
        return cls(is_valid=True)

    @classmethod
    def error(cls, error_code: BaseErrorCode, field_name: str | None = None) -> Self:
        """Build a failed validation result carrying an error code.

        Args:
            error_code: The error code describing why validation failed.
            field_name: Optional name of the offending field, for UI targeting.

        Returns:
            A failed ValidationResult.
        """
        return cls(is_valid=False, error_code=error_code, field_name=field_name)


# EOF
