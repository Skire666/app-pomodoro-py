"""Copy strategies available on models (see AGENTS.md §13.2)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from enum import Enum


class CopyModeEnum(Enum):
    """Enumerates the copy strategies a model's `copy()` method may apply."""

    E_UNSET = "UNSET"
    E_BUSINESS = "BUSINESS"
    E_TECHNICAL = "TECHNICAL"
    E_UNKNOWN = "UNKNOWN"


# EOF
