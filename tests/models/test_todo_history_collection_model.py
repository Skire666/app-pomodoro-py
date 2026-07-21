from datetime import UTC, datetime, timedelta

from pomodoro.models.todo_history_collection_model import TodoHistoryCollectionModel
from pomodoro.models.todo_history_entry_model import TodoHistoryEntryModel
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum

_BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)


def _make_entry(id_history_entry: str, changed_at: datetime) -> TodoHistoryEntryModel:
    return TodoHistoryEntryModel(
        id_history_entry=id_history_entry,
        id_todo_item="todo-1",
        id_pomodoro="pom-1",
        label_snapshot="Relire specs",
        pomodoro_name_snapshot="Sprint deep work",
        old_state=TodoStateEnum.E_IN_PROGRESS,
        new_state=TodoStateEnum.E_DONE,
        changed_at=changed_at,
    )


def test_search_most_recent_first_sorts_by_change_date_descending() -> None:
    collection = TodoHistoryCollectionModel.get_default()
    collection.create(_make_entry("h-1", _BASE_TIME))
    collection.create(_make_entry("h-2", _BASE_TIME + timedelta(hours=1)))

    results = collection.search()

    assert [entry.id_history_entry for entry in results] == ["h-2", "h-1"]


def test_purge_keeps_only_the_most_recent_entries() -> None:
    collection = TodoHistoryCollectionModel.get_default()
    for index in range(5):
        collection.create(_make_entry(f"h-{index}", _BASE_TIME + timedelta(hours=index)))

    removed = collection.purge(max_entries=3)

    assert removed == 2
    remaining_ids = {entry.id_history_entry for entry in collection}
    assert remaining_ids == {"h-2", "h-3", "h-4"}


def test_validate_fails_when_a_state_was_never_resolved() -> None:
    collection = TodoHistoryCollectionModel.get_default()
    collection.create(TodoHistoryEntryModel.get_default())

    assert collection.validate().is_valid is False


# EOF
