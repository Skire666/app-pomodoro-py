"""Global, runtime-only application state, shared across the app (see AGENTS.md §10)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from typing import Self

from pomodoro.shared.enums.main_view_enum import MainViewEnum


class AppStateModel:
    """Tracks the active main view and the global `is_busy`/`is_loading`/`is_dirty` flags.

    Unlike the persisted entities of `models/`, this is pure runtime state
    injected once from the composition root (AGENTS.md §9): it is never
    serialized to `config-pomodoro.json`, so it does not follow the
    `to_dict`/`from_dict`/`id_xxxx` contract of AGENTS.md §13.2.

    Each global flag is backed by a set of holder identifiers (typically a
    View's object name): a flag is True as long as at least one holder
    asserts it, and only returns to False once every holder has released it
    (AGENTS.md §10).
    """

    def __init__(self) -> None:
        """Initialize an idle state: no active view, every flag cleared."""
        self._active_main_view = MainViewEnum.E_UNSET
        self._busy_holders: set[str] = set()
        self._loading_holders: set[str] = set()
        self._dirty_holders: set[str] = set()

    @classmethod
    def get_default(cls) -> Self:
        """Build a fresh, idle state: no active view, every flag cleared."""
        return cls()

    @property
    def active_main_view(self) -> MainViewEnum:
        """The main navigation section currently displayed."""
        return self._active_main_view

    @active_main_view.setter
    def active_main_view(self, value: MainViewEnum) -> None:
        """Set the main navigation section currently displayed."""
        self._active_main_view = value

    @property
    def is_busy(self) -> bool:
        """True while at least one View is performing a triggered process."""
        return bool(self._busy_holders)

    @property
    def is_loading(self) -> bool:
        """True while at least one View is loading or building itself."""
        return bool(self._loading_holders)

    @property
    def is_dirty(self) -> bool:
        """True while at least one View holds an unsaved, in-progress edit."""
        return bool(self._dirty_holders)

    def set_busy(self, holder: str, is_busy: bool) -> None:
        """Register or release a busy hold from `holder`.

        Args:
            holder: Identifier of the View asserting or releasing the flag.
            is_busy: True to register the hold, False to release it.
        """
        self._update_holders(self._busy_holders, holder, is_busy)

    def set_loading(self, holder: str, is_loading: bool) -> None:
        """Register or release a loading hold from `holder`.

        Args:
            holder: Identifier of the View asserting or releasing the flag.
            is_loading: True to register the hold, False to release it.
        """
        self._update_holders(self._loading_holders, holder, is_loading)

    def set_dirty(self, holder: str, is_dirty: bool) -> None:
        """Register or release a dirty hold from `holder`.

        Args:
            holder: Identifier of the View asserting or releasing the flag.
            is_dirty: True to register the hold, False to release it.
        """
        self._update_holders(self._dirty_holders, holder, is_dirty)

    @staticmethod
    def _update_holders(holders: set[str], holder: str, asserted: bool) -> None:
        """Add or discard `holder` from `holders` depending on `asserted`."""
        if asserted:
            holders.add(holder)
        else:
            holders.discard(holder)

    def clear(self) -> None:
        """Reset this instance to its idle default state, in place."""
        self._active_main_view = MainViewEnum.E_UNSET
        self._busy_holders.clear()
        self._loading_holders.clear()
        self._dirty_holders.clear()


# EOF
