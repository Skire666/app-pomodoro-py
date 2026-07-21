from pomodoro.models.todo_item_model import TodoItemModel
from pomodoro.shared.enums.copy_mode_enum import CopyModeEnum
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum
from pomodoro.shared.errors.todo_error import ErrorCodeTodo


def test_get_default_starts_in_the_todo_state() -> None:
    item = TodoItemModel.get_default()

    assert item.state is TodoStateEnum.E_TODO


def test_validate_fails_when_label_is_empty() -> None:
    item = TodoItemModel.get_default()
    item.label = "   "

    result = item.validate()

    assert result.is_valid is False
    assert result.error_code is ErrorCodeTodo.TDI_1001


def test_to_dict_and_from_dict_round_trip_preserves_state() -> None:
    original = TodoItemModel.get_default()
    original.id_todo_item = "todo-1"
    original.id_pomodoro = "pom-1"
    original.label = "Ecrire le brief"
    original.state = TodoStateEnum.E_IN_PROGRESS

    rebuilt = TodoItemModel.from_dict(original.to_dict())

    assert rebuilt.to_dict() == original.to_dict()


def test_copy_business_mode_clears_identity_but_keeps_label_and_state() -> None:
    original = TodoItemModel.get_default()
    original.id_todo_item = "todo-1"
    original.label = "Ecrire le brief"
    original.state = TodoStateEnum.E_DONE

    clone = original.copy(CopyModeEnum.E_BUSINESS)

    assert clone.id_todo_item == ""
    assert clone.label == "Ecrire le brief"
    assert clone.state is TodoStateEnum.E_DONE


# EOF
