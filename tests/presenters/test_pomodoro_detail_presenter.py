from collections.abc import Callable

from pomodoro.models.pomodoro_detail_view_state import PomodoroDetailViewState
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.presenters.pomodoro_detail_presenter import PomodoroDetailPresenter
from pomodoro.services.pomodoro_service import PomodoroService
from pomodoro.services.todo_service import TodoService
from pomodoro.shared.validation_result import ValidationResult
from tests.conftest import FakeConfigRepository


class FakePomodoroDetailView:
    def __init__(self) -> None:
        self.is_busy = False
        self.is_loading = False
        self.enabled = True
        self.last_error: ValidationResult | None = None
        self.state: PomodoroDetailViewState | None = None
        self.callbacks: dict[str, Callable[[], None]] = {}

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def notify_error(self, rs: ValidationResult) -> None:
        self.last_error = rs

    def clear(self) -> None:
        self.state = None

    def notify_refresh(self, context: PomodoroDetailViewState) -> None:
        self.state = context

    def bind_edit_clicked(self, callback: Callable[[], None]) -> None:
        self.callbacks["edit_clicked"] = callback

    def bind_start_clicked(self, callback: Callable[[], None]) -> None:
        self.callbacks["start_clicked"] = callback


def test_show_loads_the_pomodoro_and_its_todo_count(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroDetailView()
    pomodoro_service = PomodoroService(config_repository)
    todo_service = TodoService(config_repository)
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = pomodoro_service.generate_id()
    pomodoro.name = "Sprint deep work"
    pomodoro_service.save(pomodoro)
    todo_service.add_item(pomodoro.id_pomodoro, "Ecrire le brief")
    presenter = PomodoroDetailPresenter(view, pomodoro_service, todo_service)

    presenter.show(pomodoro.id_pomodoro)

    assert view.state is not None
    assert view.state.name == "Sprint deep work"
    assert view.state.todo_count == 1


def test_show_notifies_error_for_an_unknown_pomodoro(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroDetailView()
    presenter = PomodoroDetailPresenter(view, PomodoroService(config_repository), TodoService(config_repository))

    presenter.show("missing")

    assert view.last_error is not None
    assert view.state is None


def test_edit_clicked_forwards_the_id_to_the_registered_callback(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroDetailView()
    pomodoro_service = PomodoroService(config_repository)
    todo_service = TodoService(config_repository)
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = pomodoro_service.generate_id()
    pomodoro.name = "Sprint deep work"
    pomodoro_service.save(pomodoro)
    presenter = PomodoroDetailPresenter(view, pomodoro_service, todo_service)
    presenter.show(pomodoro.id_pomodoro)
    requested: list[str] = []
    presenter.bind_edit_requested(requested.append)

    view.callbacks["edit_clicked"]()

    assert requested == [pomodoro.id_pomodoro]


# EOF
