from datetime import UTC, datetime

from pomodoro.models.app_config_model import AppConfigModel
from pomodoro.models.pomodoro_history_row_state import PomodoroHistoryRowState
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.models.todo_history_entry_model import TodoHistoryEntryModel
from pomodoro.models.todo_history_row_state import TodoHistoryRowState
from pomodoro.presenters.history_presenter import HistoryPresenter
from pomodoro.services.history_service import HistoryService
from pomodoro.services.pomodoro_service import PomodoroService
from pomodoro.shared.enums.pomodoro_history_status_enum import PomodoroHistoryStatusEnum
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum
from pomodoro.shared.validation_result import ValidationResult
from tests.conftest import FakeConfigRepository

_BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)


class FakeHistoryView:
    def __init__(self) -> None:
        self.is_busy = False
        self.is_loading = False
        self.enabled = True
        self.last_error: ValidationResult | None = None
        self.pomodoro_rows: tuple[PomodoroHistoryRowState, ...] = ()
        self.todo_rows: tuple[TodoHistoryRowState, ...] = ()

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def notify_error(self, rs: ValidationResult) -> None:
        self.last_error = rs

    def clear(self) -> None:
        self.pomodoro_rows = ()
        self.todo_rows = ()

    def notify_pomodoro_history_refresh(self, context: tuple[PomodoroHistoryRowState, ...]) -> None:
        self.pomodoro_rows = context

    def notify_todo_history_refresh(self, context: tuple[TodoHistoryRowState, ...]) -> None:
        self.todo_rows = context


def test_refresh_marks_a_pomodoro_row_as_deleted_when_its_source_no_longer_exists(
    config_repository: FakeConfigRepository,
) -> None:
    view = FakeHistoryView()
    history_service = HistoryService(config_repository)
    pomodoro_service = PomodoroService(config_repository)
    history_service.record_pomodoro_session(
        id_pomodoro="pom-missing",
        name_snapshot="Sprint deep work",
        executed_at=_BASE_TIME,
        planned_duration_seconds=1500,
        status=PomodoroHistoryStatusEnum.E_COMPLETED,
    )
    presenter = HistoryPresenter(view, history_service, pomodoro_service)

    presenter.refresh()

    assert len(view.pomodoro_rows) == 1
    assert view.pomodoro_rows[0].is_source_deleted is True


def test_refresh_does_not_mark_a_row_as_deleted_when_its_source_still_exists(
    config_repository: FakeConfigRepository,
) -> None:
    view = FakeHistoryView()
    history_service = HistoryService(config_repository)
    pomodoro_service = PomodoroService(config_repository)
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = pomodoro_service.generate_id()
    pomodoro.name = "Sprint deep work"
    pomodoro_service.save(pomodoro)
    history_service.record_pomodoro_session(
        id_pomodoro=pomodoro.id_pomodoro,
        name_snapshot=pomodoro.name,
        executed_at=_BASE_TIME,
        planned_duration_seconds=1500,
        status=PomodoroHistoryStatusEnum.E_COMPLETED,
    )
    presenter = HistoryPresenter(view, history_service, pomodoro_service)

    presenter.refresh()

    assert view.pomodoro_rows[0].is_source_deleted is False


def test_refresh_pushes_todo_history_rows(config_repository: FakeConfigRepository) -> None:
    view = FakeHistoryView()
    history_service = HistoryService(config_repository)
    pomodoro_service = PomodoroService(config_repository)
    entry = TodoHistoryEntryModel(
        id_history_entry="h-1",
        id_todo_item="todo-1",
        id_pomodoro="pom-1",
        label_snapshot="Relire specs",
        pomodoro_name_snapshot="Sprint deep work",
        old_state=TodoStateEnum.E_IN_PROGRESS,
        new_state=TodoStateEnum.E_DONE,
        changed_at=_BASE_TIME,
    )
    AppConfigModel.instance().todo_history.create(entry)
    presenter = HistoryPresenter(view, history_service, pomodoro_service)

    presenter.refresh()

    assert len(view.todo_rows) == 1
    assert view.todo_rows[0].label == "Relire specs"
    assert view.todo_rows[0].new_state is TodoStateEnum.E_DONE


# EOF
