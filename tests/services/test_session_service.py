from pomodoro.models.app_config_model import AppConfigModel
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.services.pomodoro_service import PomodoroService
from pomodoro.services.session_service import SessionService
from pomodoro.shared.enums.pomodoro_history_status_enum import PomodoroHistoryStatusEnum
from pomodoro.shared.errors.session_error import ErrorCodeSession
from tests.conftest import FakeConfigRepository


def _make_pomodoro(config_repository: FakeConfigRepository, duration_seconds: int = 1500) -> PomodoroModel:
    pomodoro_service = PomodoroService(config_repository)
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = pomodoro_service.generate_id()
    pomodoro.name = "Sprint deep work"
    pomodoro.duration_seconds = duration_seconds
    pomodoro_service.save(pomodoro)
    return pomodoro


def test_start_activates_a_session_and_stamps_last_used_at(config_repository: FakeConfigRepository) -> None:
    pomodoro = _make_pomodoro(config_repository)
    service = SessionService(config_repository)

    result = service.start(pomodoro.id_pomodoro)

    assert result.is_valid is True
    active = service.get_active()
    assert active is not None
    assert active.id_pomodoro == pomodoro.id_pomodoro
    stored = AppConfigModel.instance().pomodoros.read(pomodoro.id_pomodoro)
    assert stored is not None
    assert stored.last_used_at is not None


def test_start_fails_when_a_session_is_already_active(config_repository: FakeConfigRepository) -> None:
    pomodoro = _make_pomodoro(config_repository)
    other = _make_pomodoro(config_repository)
    service = SessionService(config_repository)
    service.start(pomodoro.id_pomodoro)

    result = service.start(other.id_pomodoro)

    assert result.is_valid is False
    assert result.error_code is ErrorCodeSession.SES_1001


def test_start_fails_for_an_unknown_pomodoro(config_repository: FakeConfigRepository) -> None:
    service = SessionService(config_repository)

    result = service.start("missing")

    assert result.is_valid is False
    assert service.get_active() is None


def test_pause_and_resume_round_trip(config_repository: FakeConfigRepository) -> None:
    pomodoro = _make_pomodoro(config_repository)
    service = SessionService(config_repository)
    service.start(pomodoro.id_pomodoro)

    pause_result = service.pause()
    active = service.get_active()

    assert pause_result.is_valid is True
    assert active is not None
    assert active.is_paused is True

    resume_result = service.resume()
    active = service.get_active()

    assert resume_result.is_valid is True
    assert active is not None
    assert active.is_paused is False


def test_pause_fails_when_no_session_is_active(config_repository: FakeConfigRepository) -> None:
    service = SessionService(config_repository)

    result = service.pause()

    assert result.is_valid is False
    assert result.error_code is ErrorCodeSession.SES_1002


def test_stop_interrupted_records_history_and_clears_the_session(config_repository: FakeConfigRepository) -> None:
    pomodoro = _make_pomodoro(config_repository)
    service = SessionService(config_repository)
    service.start(pomodoro.id_pomodoro)

    result = service.stop_interrupted()

    assert result.is_valid is True
    assert service.get_active() is None
    history = AppConfigModel.instance().pomodoro_history
    assert len(history) == 1
    assert history[0].status is PomodoroHistoryStatusEnum.E_INTERRUPTED


def test_complete_records_history_and_clears_the_session(config_repository: FakeConfigRepository) -> None:
    pomodoro = _make_pomodoro(config_repository)
    service = SessionService(config_repository)
    service.start(pomodoro.id_pomodoro)

    result = service.complete()

    assert result.is_valid is True
    assert service.get_active() is None
    history = AppConfigModel.instance().pomodoro_history
    assert len(history) == 1
    assert history[0].status is PomodoroHistoryStatusEnum.E_COMPLETED


def test_complete_fails_when_no_session_is_active(config_repository: FakeConfigRepository) -> None:
    service = SessionService(config_repository)

    result = service.complete()

    assert result.is_valid is False
    assert result.error_code is ErrorCodeSession.SES_1002


# EOF
