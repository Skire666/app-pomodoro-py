from datetime import UTC, datetime, timedelta

from pomodoro.models.pomodoro_history_collection_model import PomodoroHistoryCollectionModel
from pomodoro.models.pomodoro_history_entry_model import PomodoroHistoryEntryModel
from pomodoro.shared.enums.pomodoro_history_status_enum import PomodoroHistoryStatusEnum

_BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)


def _make_entry(
    id_history_entry: str,
    executed_at: datetime,
    status: PomodoroHistoryStatusEnum = PomodoroHistoryStatusEnum.E_COMPLETED,
) -> PomodoroHistoryEntryModel:
    return PomodoroHistoryEntryModel(
        id_history_entry=id_history_entry,
        id_pomodoro="pom-1",
        name_snapshot="Sprint deep work",
        executed_at=executed_at,
        planned_duration_seconds=1500,
        status=status,
    )


def test_search_most_recent_first_sorts_by_execution_date_descending() -> None:
    collection = PomodoroHistoryCollectionModel.get_default()
    collection.create(_make_entry("h-1", _BASE_TIME))
    collection.create(_make_entry("h-2", _BASE_TIME + timedelta(hours=1)))

    results = collection.search()

    assert [entry.id_history_entry for entry in results] == ["h-2", "h-1"]


def test_purge_keeps_only_the_most_recent_entries() -> None:
    collection = PomodoroHistoryCollectionModel.get_default()
    for index in range(5):
        collection.create(_make_entry(f"h-{index}", _BASE_TIME + timedelta(hours=index)))

    removed = collection.purge(max_entries=3)

    assert removed == 2
    remaining_ids = {entry.id_history_entry for entry in collection}
    assert remaining_ids == {"h-2", "h-3", "h-4"}


def test_purge_is_a_no_op_when_under_the_limit() -> None:
    collection = PomodoroHistoryCollectionModel.get_default()
    collection.create(_make_entry("h-1", _BASE_TIME))

    removed = collection.purge(max_entries=100)

    assert removed == 0
    assert len(collection) == 1


def test_validate_fails_when_status_was_never_resolved() -> None:
    collection = PomodoroHistoryCollectionModel.get_default()
    collection.create(PomodoroHistoryEntryModel.get_default())

    result = collection.validate()

    assert result.is_valid is False


def test_validate_succeeds_once_status_is_resolved() -> None:
    collection = PomodoroHistoryCollectionModel.get_default()
    collection.create(_make_entry("h-1", _BASE_TIME))

    assert collection.validate().is_valid is True


# EOF
