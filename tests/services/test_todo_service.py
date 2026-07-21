from pomodoro.models.app_config_model import AppConfigModel
from pomodoro.services.todo_service import TodoService
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum
from pomodoro.shared.errors.todo_error import ErrorCodeTodo
from tests.conftest import FakeConfigRepository


def test_add_item_rejects_an_empty_label(config_repository: FakeConfigRepository) -> None:
    service = TodoService(config_repository)

    result = service.add_item("pom-1", "   ")

    assert result.is_valid is False
    assert result.error_code is ErrorCodeTodo.TDI_1001
    assert service.list_for_pomodoro("pom-1") == ()


def test_add_item_starts_in_the_todo_state(config_repository: FakeConfigRepository) -> None:
    service = TodoService(config_repository)

    service.add_item("pom-1", "Ecrire le brief")

    items = service.list_for_pomodoro("pom-1")
    assert len(items) == 1
    assert items[0].state is TodoStateEnum.E_TODO


def test_rename_item_fails_for_an_unknown_item(config_repository: FakeConfigRepository) -> None:
    service = TodoService(config_repository)

    result = service.rename_item("missing", "New label")

    assert result.is_valid is False


def test_change_state_records_a_history_entry(config_repository: FakeConfigRepository) -> None:
    service = TodoService(config_repository)
    service.add_item("pom-1", "Ecrire le brief")
    item = service.list_for_pomodoro("pom-1")[0]

    result = service.change_state(item.id_todo_item, TodoStateEnum.E_IN_PROGRESS)

    assert result.is_valid is True
    history = AppConfigModel.instance().todo_history
    assert len(history) == 1
    entry = history[0]
    assert entry.old_state is TodoStateEnum.E_TODO
    assert entry.new_state is TodoStateEnum.E_IN_PROGRESS


def test_change_state_to_the_same_state_is_a_no_op(config_repository: FakeConfigRepository) -> None:
    service = TodoService(config_repository)
    service.add_item("pom-1", "Ecrire le brief")
    item = service.list_for_pomodoro("pom-1")[0]

    service.change_state(item.id_todo_item, TodoStateEnum.E_TODO)

    assert len(AppConfigModel.instance().todo_history) == 0


def test_duplicate_item_resets_state_and_suffixes_the_label(config_repository: FakeConfigRepository) -> None:
    service = TodoService(config_repository)
    service.add_item("pom-1", "Ecrire le brief")
    item = service.list_for_pomodoro("pom-1")[0]
    service.change_state(item.id_todo_item, TodoStateEnum.E_DONE)

    clone = service.duplicate_item(item.id_todo_item)

    assert clone is not None
    assert clone.id_todo_item != item.id_todo_item
    assert clone.label == "Ecrire le brief (copie)"
    assert clone.state is TodoStateEnum.E_TODO


def test_delete_list_removes_every_item_for_the_pomodoro(config_repository: FakeConfigRepository) -> None:
    service = TodoService(config_repository)
    service.add_item("pom-1", "Item A")
    service.add_item("pom-1", "Item B")
    service.add_item("pom-2", "Item C")

    removed = service.delete_list("pom-1")

    assert removed == 2
    assert service.list_for_pomodoro("pom-1") == ()
    assert len(service.list_for_pomodoro("pom-2")) == 1


def test_delete_item_returns_the_removed_item(config_repository: FakeConfigRepository) -> None:
    service = TodoService(config_repository)
    service.add_item("pom-1", "Ecrire le brief")
    item = service.list_for_pomodoro("pom-1")[0]

    removed = service.delete_item(item.id_todo_item)

    assert removed is not None
    assert removed.label == "Ecrire le brief"
    assert service.list_for_pomodoro("pom-1") == ()


def test_delete_item_returns_none_for_an_unknown_item(config_repository: FakeConfigRepository) -> None:
    service = TodoService(config_repository)

    assert service.delete_item("missing") is None


def test_restore_item_reinserts_it_unchanged(config_repository: FakeConfigRepository) -> None:
    service = TodoService(config_repository)
    service.add_item("pom-1", "Ecrire le brief")
    item = service.list_for_pomodoro("pom-1")[0]
    service.delete_item(item.id_todo_item)

    result = service.restore_item(item)

    assert result.is_valid is True
    restored = service.list_for_pomodoro("pom-1")
    assert len(restored) == 1
    assert restored[0].id_todo_item == item.id_todo_item


# EOF
