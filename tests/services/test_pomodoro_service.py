from pomodoro.models.app_config_model import AppConfigModel
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.models.todo_item_model import TodoItemModel
from pomodoro.services.pomodoro_service import PomodoroService
from pomodoro.shared.errors.pomodoro_error import ErrorCodePomodoro
from tests.conftest import FakeConfigRepository


def test_save_rejects_a_pomodoro_with_an_empty_name(config_repository: FakeConfigRepository) -> None:
    service = PomodoroService(config_repository)
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = service.generate_id()

    result = service.save(pomodoro)

    assert result.is_valid is False
    assert result.error_code is ErrorCodePomodoro.POM_1001
    assert service.get(pomodoro.id_pomodoro) is None
    assert config_repository.save_count == 0


def test_save_creates_a_new_pomodoro_and_persists_it(config_repository: FakeConfigRepository) -> None:
    service = PomodoroService(config_repository)
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = service.generate_id()
    pomodoro.name = "Sprint deep work"

    result = service.save(pomodoro)

    assert result.is_valid is True
    assert service.get(pomodoro.id_pomodoro) is not None
    assert config_repository.save_count == 1


def test_save_updates_an_existing_pomodoro(config_repository: FakeConfigRepository) -> None:
    service = PomodoroService(config_repository)
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = service.generate_id()
    pomodoro.name = "Sprint deep work"
    service.save(pomodoro)

    pomodoro.name = "Renamed"
    service.save(pomodoro)

    stored = service.get(pomodoro.id_pomodoro)
    assert stored is not None
    assert stored.name == "Renamed"
    assert config_repository.save_count == 2


def test_duplicate_creates_a_copy_with_a_new_identity(config_repository: FakeConfigRepository) -> None:
    service = PomodoroService(config_repository)
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = service.generate_id()
    pomodoro.name = "Sprint deep work"
    service.save(pomodoro)

    clone = service.duplicate(pomodoro.id_pomodoro)

    assert clone is not None
    assert clone.id_pomodoro != pomodoro.id_pomodoro
    assert clone.name == "Sprint deep work"
    assert len(AppConfigModel.instance().pomodoros) == 2


def test_delete_is_blocked_while_a_session_is_active(config_repository: FakeConfigRepository) -> None:
    service = PomodoroService(config_repository)
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = service.generate_id()
    pomodoro.name = "Sprint deep work"
    service.save(pomodoro)

    result = service.delete(pomodoro.id_pomodoro, has_active_session=True)

    assert result.is_valid is False
    assert result.error_code is ErrorCodePomodoro.POM_1003
    assert service.get(pomodoro.id_pomodoro) is not None


def test_delete_removes_the_pomodoro_and_its_todo_items(config_repository: FakeConfigRepository) -> None:
    service = PomodoroService(config_repository)
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = service.generate_id()
    pomodoro.name = "Sprint deep work"
    service.save(pomodoro)
    AppConfigModel.instance().todos.create(_todo_for(pomodoro.id_pomodoro))

    result = service.delete(pomodoro.id_pomodoro, has_active_session=False)

    assert result.is_valid is True
    assert service.get(pomodoro.id_pomodoro) is None
    assert AppConfigModel.instance().todos.for_pomodoro(pomodoro.id_pomodoro) == ()


def _todo_for(id_pomodoro: str) -> TodoItemModel:
    item = TodoItemModel.get_default()
    item.id_todo_item = "todo-1"
    item.id_pomodoro = id_pomodoro
    item.label = "Ecrire le brief"
    return item


# EOF
