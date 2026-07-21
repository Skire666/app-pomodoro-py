from collections.abc import Callable

from pomodoro.models.pomodoro_list_view_state import PomodoroListViewState
from pomodoro.models.pomodoro_row_state import PomodoroRowState
from pomodoro.shared.enums.pomodoro_sort_mode_enum import PomodoroSortModeEnum
from pomodoro.shared.validation_result import ValidationResult


class FakePomodoroListView:
    def __init__(self) -> None:
        self.is_dirty = False
        self.is_busy = False
        self.is_loading = False
        self.enabled = True
        self.last_error: ValidationResult | None = None
        self.rows: tuple[PomodoroRowState, ...] = ()
        self._state = PomodoroListViewState(search_text="", sort_mode=PomodoroSortModeEnum.E_UNSET)
        self.callbacks: dict[str, Callable[..., None]] = {}

    def snapshot(self) -> PomodoroListViewState:
        return self._state

    def set_search_state(self, state: PomodoroListViewState) -> None:
        self._state = state

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def notify_error(self, rs: ValidationResult) -> None:
        self.last_error = rs

    def clear(self) -> None:
        self.rows = ()

    def notify_refresh(self, context: tuple[PomodoroRowState, ...]) -> None:
        self.rows = context

    def bind_search_changed(self, callback: Callable[[str], None]) -> None:
        self.callbacks["search_changed"] = callback

    def bind_sort_changed(self, callback: Callable[[PomodoroSortModeEnum], None]) -> None:
        self.callbacks["sort_changed"] = callback

    def bind_new_clicked(self, callback: Callable[[], None]) -> None:
        self.callbacks["new_clicked"] = callback

    def bind_item_start_clicked(self, callback: Callable[[str], None]) -> None:
        self.callbacks["item_start_clicked"] = callback

    def bind_item_edit_clicked(self, callback: Callable[[str], None]) -> None:
        self.callbacks["item_edit_clicked"] = callback

    def bind_item_duplicate_clicked(self, callback: Callable[[str], None]) -> None:
        self.callbacks["item_duplicate_clicked"] = callback

    def bind_item_delete_clicked(self, callback: Callable[[str], None]) -> None:
        self.callbacks["item_delete_clicked"] = callback


# EOF
