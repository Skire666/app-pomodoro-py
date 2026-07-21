from datetime import UTC, datetime

from pomodoro.models.pomodoro_collection_model import PomodoroCollectionModel
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.shared.enums.pomodoro_sort_mode_enum import PomodoroSortModeEnum


def _make_pomodoro(id_pomodoro: str, name: str, *, duration_seconds: int = 60) -> PomodoroModel:
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = id_pomodoro
    pomodoro.name = name
    pomodoro.duration_seconds = duration_seconds
    return pomodoro


def test_create_then_read_returns_the_stored_pomodoro() -> None:
    collection = PomodoroCollectionModel.get_default()
    pomodoro = _make_pomodoro("pom-1", "Sprint deep work")

    collection.create(pomodoro)

    assert collection.read("pom-1") is pomodoro
    assert len(collection) == 1


def test_read_returns_none_for_an_unknown_id() -> None:
    collection = PomodoroCollectionModel.get_default()

    assert collection.read("missing") is None


def test_update_replaces_the_matching_entry() -> None:
    collection = PomodoroCollectionModel.get_default()
    collection.create(_make_pomodoro("pom-1", "Sprint deep work"))
    replacement = _make_pomodoro("pom-1", "Renamed")

    updated = collection.update(replacement)
    stored = collection.read("pom-1")

    assert updated is True
    assert stored is not None
    assert stored.name == "Renamed"


def test_delete_removes_the_matching_entry() -> None:
    collection = PomodoroCollectionModel.get_default()
    collection.create(_make_pomodoro("pom-1", "Sprint deep work"))

    deleted = collection.delete("pom-1")

    assert deleted is True
    assert len(collection) == 0


def test_search_default_sort_is_alphabetical() -> None:
    collection = PomodoroCollectionModel.get_default()
    collection.create(_make_pomodoro("pom-1", "Zeta"))
    collection.create(_make_pomodoro("pom-2", "Alpha"))
    collection.create(_make_pomodoro("pom-3", "Beta"))

    results = collection.search()

    assert [item.id_pomodoro for item in results] == ["pom-2", "pom-3", "pom-1"]


def test_search_sort_by_duration_is_ascending() -> None:
    collection = PomodoroCollectionModel.get_default()
    collection.create(_make_pomodoro("pom-1", "A", duration_seconds=300))
    collection.create(_make_pomodoro("pom-2", "B", duration_seconds=100))

    results = collection.search(sort_mode=PomodoroSortModeEnum.E_DURATION)

    assert [item.id_pomodoro for item in results] == ["pom-2", "pom-1"]


def test_search_sort_by_last_used_puts_never_used_items_last() -> None:
    collection = PomodoroCollectionModel.get_default()
    used = _make_pomodoro("pom-1", "Used")
    used.last_used_at = datetime(2026, 1, 1, tzinfo=UTC)
    never_used = _make_pomodoro("pom-2", "Never")
    collection.create(never_used)
    collection.create(used)

    results = collection.search(sort_mode=PomodoroSortModeEnum.E_LAST_USED)

    assert [item.id_pomodoro for item in results] == ["pom-1", "pom-2"]


def test_serialize_and_deserialize_round_trip_preserves_items() -> None:
    collection = PomodoroCollectionModel.get_default()
    collection.create(_make_pomodoro("pom-1", "Sprint deep work"))

    rebuilt = PomodoroCollectionModel.deserialize(collection.serialize())

    assert len(rebuilt) == 1
    assert rebuilt.read("pom-1") is not None


# EOF
