from pomodoro.models.todo_collection_model import TodoCollectionModel
from pomodoro.models.todo_item_model import TodoItemModel
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum


def _make_item(id_todo_item: str, id_pomodoro: str, state: TodoStateEnum = TodoStateEnum.E_TODO) -> TodoItemModel:
    item = TodoItemModel.get_default()
    item.id_todo_item = id_todo_item
    item.id_pomodoro = id_pomodoro
    item.label = id_todo_item
    item.state = state
    return item


def test_for_pomodoro_returns_only_items_owned_by_that_pomodoro() -> None:
    collection = TodoCollectionModel.get_default()
    collection.create(_make_item("todo-1", "pom-1"))
    collection.create(_make_item("todo-2", "pom-2"))

    scoped = collection.for_pomodoro("pom-1")

    assert [item.id_todo_item for item in scoped] == ["todo-1"]


def test_count_active_for_pomodoro_excludes_cancelled_items() -> None:
    collection = TodoCollectionModel.get_default()
    collection.create(_make_item("todo-1", "pom-1", TodoStateEnum.E_TODO))
    collection.create(_make_item("todo-2", "pom-1", TodoStateEnum.E_CANCELLED))

    assert collection.count_active_for_pomodoro("pom-1") == 1


def test_delete_for_pomodoro_removes_every_owned_item_and_returns_the_count() -> None:
    collection = TodoCollectionModel.get_default()
    collection.create(_make_item("todo-1", "pom-1"))
    collection.create(_make_item("todo-2", "pom-1"))
    collection.create(_make_item("todo-3", "pom-2"))

    removed = collection.delete_for_pomodoro("pom-1")

    assert removed == 2
    assert len(collection) == 1
    assert collection.read("todo-3") is not None


# EOF
