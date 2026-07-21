from datetime import UTC, datetime, timedelta

from pomodoro.models.app_config_model import MAX_POMODORO_HISTORY_ENTRIES
from pomodoro.services.history_service import HistoryService
from pomodoro.shared.enums.pomodoro_history_status_enum import PomodoroHistoryStatusEnum
from tests.conftest import FakeConfigRepository

_BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)


def test_record_pomodoro_session_persists_and_returns_the_entry(config_repository: FakeConfigRepository) -> None:
    service = HistoryService(config_repository)

    entry = service.record_pomodoro_session(
        id_pomodoro="pom-1",
        name_snapshot="Sprint deep work",
        executed_at=_BASE_TIME,
        planned_duration_seconds=1500,
        status=PomodoroHistoryStatusEnum.E_COMPLETED,
    )

    assert entry.status is PomodoroHistoryStatusEnum.E_COMPLETED
    assert config_repository.save_count == 1
    assert service.list_pomodoro_history() == (entry,)


def test_list_pomodoro_history_returns_most_recent_first(config_repository: FakeConfigRepository) -> None:
    service = HistoryService(config_repository)
    older = service.record_pomodoro_session(
        id_pomodoro="pom-1",
        name_snapshot="Older",
        executed_at=_BASE_TIME,
        planned_duration_seconds=1500,
        status=PomodoroHistoryStatusEnum.E_COMPLETED,
    )
    newer = service.record_pomodoro_session(
        id_pomodoro="pom-1",
        name_snapshot="Newer",
        executed_at=_BASE_TIME + timedelta(hours=1),
        planned_duration_seconds=1500,
        status=PomodoroHistoryStatusEnum.E_COMPLETED,
    )

    assert service.list_pomodoro_history() == (newer, older)


def test_record_pomodoro_session_purges_entries_beyond_the_limit(config_repository: FakeConfigRepository) -> None:
    service = HistoryService(config_repository)
    for index in range(MAX_POMODORO_HISTORY_ENTRIES + 5):
        service.record_pomodoro_session(
            id_pomodoro="pom-1",
            name_snapshot=f"Session {index}",
            executed_at=_BASE_TIME + timedelta(hours=index),
            planned_duration_seconds=1500,
            status=PomodoroHistoryStatusEnum.E_COMPLETED,
        )

    assert len(service.list_pomodoro_history()) == MAX_POMODORO_HISTORY_ENTRIES


# EOF
