from pomodoro.models.pomodoro_list_view_state import PomodoroListViewState
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.presenters.pomodoro_list_presenter import PomodoroListPresenter
from pomodoro.services.pomodoro_service import PomodoroService
from pomodoro.shared.enums.pomodoro_sort_mode_enum import PomodoroSortModeEnum
from pomodoro.shared.errors.pomodoro_error import ErrorCodePomodoro
from tests.conftest import FakeConfigRepository
from tests.presenters.conftest import FakePomodoroListView


def _make_pomodoro(service: PomodoroService, name: str) -> PomodoroModel:
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = service.generate_id()
    pomodoro.name = name
    service.save(pomodoro)
    return pomodoro


def test_construction_pushes_no_rows_until_refresh_is_requested(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroListView()
    service = PomodoroService(config_repository)

    PomodoroListPresenter(view, service)

    assert view.rows == ()


def test_search_changed_refreshes_the_view_with_matching_rows(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroListView()
    service = PomodoroService(config_repository)
    _make_pomodoro(service, "Sprint deep work")
    _make_pomodoro(service, "Pause café")
    presenter = PomodoroListPresenter(view, service)
    search_state = PomodoroListViewState(search_text="Sprint", sort_mode=PomodoroSortModeEnum.E_UNSET)
    view.set_search_state(search_state)

    view.callbacks["search_changed"]("Sprint")

    assert [row.name for row in view.rows] == ["Sprint deep work"]
    assert presenter is not None


def test_item_delete_clicked_is_blocked_when_a_session_is_active(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroListView()
    service = PomodoroService(config_repository)
    pomodoro = _make_pomodoro(service, "Sprint deep work")
    PomodoroListPresenter(view, service, is_session_active_for=lambda _id: True)

    view.callbacks["item_delete_clicked"](pomodoro.id_pomodoro)

    assert view.last_error is not None
    assert view.last_error.error_code is ErrorCodePomodoro.POM_1003
    assert service.get(pomodoro.id_pomodoro) is not None


def test_item_delete_clicked_removes_the_pomodoro_when_no_session_is_active(
    config_repository: FakeConfigRepository,
) -> None:
    view = FakePomodoroListView()
    service = PomodoroService(config_repository)
    pomodoro = _make_pomodoro(service, "Sprint deep work")
    PomodoroListPresenter(view, service)

    view.callbacks["item_delete_clicked"](pomodoro.id_pomodoro)

    assert view.rows == ()
    assert service.get(pomodoro.id_pomodoro) is None


def test_item_duplicate_clicked_adds_a_second_row(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroListView()
    service = PomodoroService(config_repository)
    pomodoro = _make_pomodoro(service, "Sprint deep work")
    PomodoroListPresenter(view, service)

    view.callbacks["item_duplicate_clicked"](pomodoro.id_pomodoro)

    assert len(view.rows) == 2


def test_new_clicked_forwards_to_the_registered_callback(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroListView()
    service = PomodoroService(config_repository)
    presenter = PomodoroListPresenter(view, service)
    calls: list[None] = []
    presenter.bind_new_requested(lambda: calls.append(None))

    view.callbacks["new_clicked"]()

    assert len(calls) == 1


# EOF
