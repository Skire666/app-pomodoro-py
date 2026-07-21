from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from pomodoro.models.active_session_model import ActiveSessionModel
from pomodoro.models.active_session_view_state import ActiveSessionViewState
from pomodoro.models.app_config_model import AppConfigModel
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.presenters.active_session_presenter import ActiveSessionPresenter
from pomodoro.services.pomodoro_service import PomodoroService
from pomodoro.services.session_service import SessionService
from pomodoro.shared.validation_result import ValidationResult
from tests.conftest import FakeConfigRepository


class FakeActiveSessionView:
    def __init__(self) -> None:
        self.is_busy = False
        self.is_loading = False
        self.enabled = True
        self.last_error: ValidationResult | None = None
        self.state: ActiveSessionViewState | None = None
        self.last_tick: tuple[int, bool] | None = None
        self.played_sound: tuple[str, int, int, int] | None = None
        self.sound_stopped_count = 0
        self.callbacks: dict[str, Callable[[], None]] = {}

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def notify_error(self, rs: ValidationResult) -> None:
        self.last_error = rs

    def clear(self) -> None:
        self.state = None

    def notify_refresh(self, context: ActiveSessionViewState) -> None:
        self.state = context

    def notify_tick(self, remaining_seconds: int, is_paused: bool) -> None:
        self.last_tick = (remaining_seconds, is_paused)

    def play_completion_sound(
        self, sound_path: str, volume: int, repeat_count: int, repeat_interval_seconds: int
    ) -> None:
        self.played_sound = (sound_path, volume, repeat_count, repeat_interval_seconds)

    def stop_completion_sound(self) -> None:
        self.sound_stopped_count += 1

    def bind_tick_requested(self, callback: Callable[[], None]) -> None:
        self.callbacks["tick_requested"] = callback

    def bind_edit_clicked(self, callback: Callable[[], None]) -> None:
        self.callbacks["edit_clicked"] = callback

    def bind_play_clicked(self, callback: Callable[[], None]) -> None:
        self.callbacks["play_clicked"] = callback

    def bind_pause_clicked(self, callback: Callable[[], None]) -> None:
        self.callbacks["pause_clicked"] = callback

    def bind_reset_clicked(self, callback: Callable[[], None]) -> None:
        self.callbacks["reset_clicked"] = callback


def _start_session(config_repository: FakeConfigRepository, *, duration_seconds: int = 1500) -> str:
    pomodoro_service = PomodoroService(config_repository)
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = pomodoro_service.generate_id()
    pomodoro.name = "Sprint deep work"
    pomodoro.duration_seconds = duration_seconds
    pomodoro.sound_path = "son_cloche.mp3"
    pomodoro_service.save(pomodoro)
    SessionService(config_repository).start(pomodoro.id_pomodoro)
    return pomodoro.id_pomodoro


def _expire_active_session(duration_seconds: int) -> None:
    """Rewind the active session's clock so it now reads as complete."""
    config = AppConfigModel.instance()
    session = config.active_session
    assert session is not None
    now = datetime.now(UTC)
    config.active_session = ActiveSessionModel(
        id_pomodoro=session.id_pomodoro,
        name_snapshot=session.name_snapshot,
        planned_duration_seconds=session.planned_duration_seconds,
        accumulated_seconds=0,
        is_paused=False,
        last_resumed_at=now - timedelta(seconds=duration_seconds + 10),
        created_at=session.created_at,
        modified_at=now,
    )


def test_show_notifies_error_when_no_session_is_active(config_repository: FakeConfigRepository) -> None:
    view = FakeActiveSessionView()
    presenter = ActiveSessionPresenter(view, SessionService(config_repository), PomodoroService(config_repository))

    presenter.show()

    assert view.last_error is not None
    assert view.state is None


def test_show_loads_the_active_session(config_repository: FakeConfigRepository) -> None:
    view = FakeActiveSessionView()
    _start_session(config_repository, duration_seconds=1500)
    presenter = ActiveSessionPresenter(view, SessionService(config_repository), PomodoroService(config_repository))

    presenter.show()

    assert view.state is not None
    assert view.state.name == "Sprint deep work"
    assert view.state.planned_duration_seconds == 1500


def test_pause_then_tick_reports_the_frozen_remaining_time(config_repository: FakeConfigRepository) -> None:
    view = FakeActiveSessionView()
    _start_session(config_repository, duration_seconds=1500)
    presenter = ActiveSessionPresenter(view, SessionService(config_repository), PomodoroService(config_repository))
    presenter.show()

    view.callbacks["pause_clicked"]()
    view.callbacks["tick_requested"]()

    assert view.last_tick is not None
    assert view.last_tick[1] is True


def test_play_clicked_resumes_a_paused_session(config_repository: FakeConfigRepository) -> None:
    view = FakeActiveSessionView()
    _start_session(config_repository, duration_seconds=1500)
    presenter = ActiveSessionPresenter(view, SessionService(config_repository), PomodoroService(config_repository))
    presenter.show()
    view.callbacks["pause_clicked"]()

    view.callbacks["play_clicked"]()

    assert view.last_tick is not None
    assert view.last_tick[1] is False


def test_reset_clicked_restores_the_full_planned_duration(config_repository: FakeConfigRepository) -> None:
    view = FakeActiveSessionView()
    session_service = SessionService(config_repository)
    _start_session(config_repository, duration_seconds=1500)
    presenter = ActiveSessionPresenter(view, session_service, PomodoroService(config_repository))
    presenter.show()
    active = session_service.get_active()
    assert active is not None
    active.pause(datetime.now(UTC) + timedelta(seconds=100))  # simulate 100s of elapsed running time

    view.callbacks["reset_clicked"]()

    assert view.last_tick is not None
    assert view.last_tick[0] == 1500


def test_tick_past_the_planned_duration_starts_the_alarm_without_completing(
    config_repository: FakeConfigRepository,
) -> None:
    view = FakeActiveSessionView()
    session_service = SessionService(config_repository)
    _start_session(config_repository, duration_seconds=60)
    presenter = ActiveSessionPresenter(view, session_service, PomodoroService(config_repository))
    presenter.show()
    _expire_active_session(duration_seconds=60)

    view.callbacks["tick_requested"]()

    assert view.played_sound is not None
    assert view.played_sound[0] == "son_cloche.mp3"
    assert session_service.get_active() is not None


def test_tick_keeps_counting_into_the_negative_past_completion(config_repository: FakeConfigRepository) -> None:
    view = FakeActiveSessionView()
    session_service = SessionService(config_repository)
    _start_session(config_repository, duration_seconds=60)
    presenter = ActiveSessionPresenter(view, session_service, PomodoroService(config_repository))
    presenter.show()
    _expire_active_session(duration_seconds=60)

    view.callbacks["tick_requested"]()

    assert view.last_tick is not None
    assert view.last_tick[0] < 0


def test_further_ticks_past_completion_do_not_replay_the_alarm(config_repository: FakeConfigRepository) -> None:
    view = FakeActiveSessionView()
    session_service = SessionService(config_repository)
    _start_session(config_repository, duration_seconds=60)
    presenter = ActiveSessionPresenter(view, session_service, PomodoroService(config_repository))
    presenter.show()
    _expire_active_session(duration_seconds=60)
    view.callbacks["tick_requested"]()
    view.played_sound = None

    view.callbacks["tick_requested"]()

    assert view.played_sound is None


def test_pause_clicked_while_ringing_silences_the_alarm_and_pauses(
    config_repository: FakeConfigRepository,
) -> None:
    view = FakeActiveSessionView()
    session_service = SessionService(config_repository)
    _start_session(config_repository, duration_seconds=60)
    presenter = ActiveSessionPresenter(view, session_service, PomodoroService(config_repository))
    presenter.show()
    _expire_active_session(duration_seconds=60)
    view.callbacks["tick_requested"]()

    view.callbacks["pause_clicked"]()

    assert view.sound_stopped_count == 1
    active = session_service.get_active()
    assert active is not None
    assert active.is_paused is True


def test_reset_clicked_while_ringing_silences_the_alarm_and_restores_the_full_duration(
    config_repository: FakeConfigRepository,
) -> None:
    view = FakeActiveSessionView()
    session_service = SessionService(config_repository)
    _start_session(config_repository, duration_seconds=60)
    presenter = ActiveSessionPresenter(view, session_service, PomodoroService(config_repository))
    presenter.show()
    _expire_active_session(duration_seconds=60)
    view.callbacks["tick_requested"]()

    view.callbacks["reset_clicked"]()

    assert view.sound_stopped_count == 1
    assert view.last_tick is not None
    assert view.last_tick[0] == 60


def test_edit_clicked_while_ringing_silences_the_alarm_and_still_forwards_the_id(
    config_repository: FakeConfigRepository,
) -> None:
    view = FakeActiveSessionView()
    session_service = SessionService(config_repository)
    id_pomodoro = _start_session(config_repository, duration_seconds=60)
    presenter = ActiveSessionPresenter(view, session_service, PomodoroService(config_repository))
    presenter.show()
    _expire_active_session(duration_seconds=60)
    view.callbacks["tick_requested"]()
    requested: list[str] = []
    presenter.bind_edit_requested(requested.append)

    view.callbacks["edit_clicked"]()

    assert view.sound_stopped_count == 1
    assert session_service.get_active() is not None
    assert requested == [id_pomodoro]


def test_edit_clicked_forwards_the_id_to_the_registered_callback(config_repository: FakeConfigRepository) -> None:
    view = FakeActiveSessionView()
    presenter = ActiveSessionPresenter(view, SessionService(config_repository), PomodoroService(config_repository))
    id_pomodoro = _start_session(config_repository, duration_seconds=1500)
    presenter.show()
    requested: list[str] = []
    presenter.bind_edit_requested(requested.append)

    view.callbacks["edit_clicked"]()

    assert requested == [id_pomodoro]


# EOF
