from collections.abc import Callable

from pomodoro.models.pomodoro_edit_view_state import PomodoroEditViewState
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.presenters.pomodoro_edit_presenter import (
    DEFAULT_NEW_POMODORO_DURATION_SECONDS,
    PomodoroEditPresenter,
)
from pomodoro.services.pomodoro_service import PomodoroService
from pomodoro.shared import i18n_fra
from pomodoro.shared.errors.pomodoro_error import ErrorCodePomodoro
from pomodoro.shared.errors.sound_error import ErrorCodeSound
from pomodoro.shared.validation_result import ValidationResult
from tests.conftest import FakeConfigRepository


class FakeSoundService:
    def __init__(self, *, available: bool = True) -> None:
        self.available = available
        self.checked_paths: list[str | None] = []

    def check_available(self, sound_path: str | None) -> ValidationResult:
        self.checked_paths.append(sound_path)
        if sound_path is None or self.available:
            return ValidationResult.ok()
        return ValidationResult.error(ErrorCodeSound.SND_1001)


class FakePomodoroEditView:
    def __init__(self) -> None:
        self.is_dirty = False
        self.is_busy = False
        self.is_loading = False
        self.enabled = True
        self.last_error: ValidationResult | None = None
        self.loaded: PomodoroModel | None = None
        self.saved_count = 0
        self.cleared = False
        self.played: tuple[str, int] | None = None
        self._state = PomodoroEditViewState(
            name="",
            duration_seconds=1500,
            sound_path=None,
            sound_volume=80,
            sound_repeat_count=1,
            sound_repeat_interval_seconds=10,
        )
        self.callbacks: dict[str, Callable[[], None]] = {}

    def snapshot(self) -> PomodoroEditViewState:
        return self._state

    def set_state(self, state: PomodoroEditViewState) -> None:
        self._state = state

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def notify_error(self, rs: ValidationResult) -> None:
        self.last_error = rs

    def clear(self) -> None:
        self.cleared = True

    def notify_refresh(self, context: PomodoroModel) -> None:
        self.loaded = context

    def notify_saved(self) -> None:
        self.saved_count += 1

    def play_preview(self, sound_path: str, volume: int) -> None:
        self.played = (sound_path, volume)

    def bind_field_changed(self, callback: Callable[[], None]) -> None:
        self.callbacks["field_changed"] = callback

    def bind_test_sound_clicked(self, callback: Callable[[], None]) -> None:
        self.callbacks["test_sound_clicked"] = callback

    def bind_close_clicked(self, callback: Callable[[], None]) -> None:
        self.callbacks["close_clicked"] = callback


def test_start_create_generates_an_id_and_loads_a_default_pomodoro(
    config_repository: FakeConfigRepository,
) -> None:
    view = FakePomodoroEditView()
    presenter = PomodoroEditPresenter(view, PomodoroService(config_repository), FakeSoundService())

    presenter.start_create()

    assert view.cleared is True
    assert view.loaded is not None
    assert view.loaded.id_pomodoro == ""
    assert view.loaded.name == i18n_fra.FORM_DEFAULT_NAME
    assert view.loaded.duration_seconds == DEFAULT_NEW_POMODORO_DURATION_SECONDS


def test_field_changed_before_start_is_a_no_op(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroEditView()
    PomodoroEditPresenter(view, PomodoroService(config_repository), FakeSoundService())

    view.callbacks["field_changed"]()

    assert view.saved_count == 0
    assert view.last_error is None


def test_field_changed_saves_and_notifies_saved_on_success(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroEditView()
    presenter = PomodoroEditPresenter(view, PomodoroService(config_repository), FakeSoundService())
    presenter.start_create()
    view.set_state(
        PomodoroEditViewState(
            name="Sprint deep work",
            duration_seconds=1500,
            sound_path=None,
            sound_volume=80,
            sound_repeat_count=1,
            sound_repeat_interval_seconds=10,
        )
    )

    view.callbacks["field_changed"]()

    assert view.saved_count == 1
    assert view.last_error is None


def test_field_changed_reports_validation_error_without_saving(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroEditView()
    presenter = PomodoroEditPresenter(view, PomodoroService(config_repository), FakeSoundService())
    presenter.start_create()

    view.callbacks["field_changed"]()

    assert view.saved_count == 0
    assert view.last_error is not None
    assert view.last_error.error_code is ErrorCodePomodoro.POM_1001


def test_start_edit_loads_the_existing_pomodoro(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroEditView()
    service = PomodoroService(config_repository)
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = service.generate_id()
    pomodoro.name = "Sprint deep work"
    service.save(pomodoro)
    presenter = PomodoroEditPresenter(view, service, FakeSoundService())

    presenter.start_edit(pomodoro.id_pomodoro)

    assert view.loaded is not None
    assert view.loaded.name == "Sprint deep work"


def test_start_edit_notifies_error_for_an_unknown_pomodoro(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroEditView()
    presenter = PomodoroEditPresenter(view, PomodoroService(config_repository), FakeSoundService())

    presenter.start_edit("missing")

    assert view.last_error is not None
    assert view.loaded is None


def test_test_sound_clicked_plays_the_preview_when_available(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroEditView()
    view.set_state(
        PomodoroEditViewState(
            name="Sprint deep work",
            duration_seconds=1500,
            sound_path="son_cloche.mp3",
            sound_volume=80,
            sound_repeat_count=1,
            sound_repeat_interval_seconds=10,
        )
    )
    PomodoroEditPresenter(view, PomodoroService(config_repository), FakeSoundService(available=True))

    view.callbacks["test_sound_clicked"]()

    assert view.played == ("son_cloche.mp3", 80)
    assert view.last_error is None


def test_test_sound_clicked_notifies_error_when_the_file_is_missing(
    config_repository: FakeConfigRepository,
) -> None:
    view = FakePomodoroEditView()
    view.set_state(
        PomodoroEditViewState(
            name="Sprint deep work",
            duration_seconds=1500,
            sound_path="missing.mp3",
            sound_volume=80,
            sound_repeat_count=1,
            sound_repeat_interval_seconds=10,
        )
    )
    PomodoroEditPresenter(view, PomodoroService(config_repository), FakeSoundService(available=False))

    view.callbacks["test_sound_clicked"]()

    assert view.played is None
    assert view.last_error is not None
    assert view.last_error.error_code is ErrorCodeSound.SND_1001


def test_close_clicked_forwards_to_the_registered_callback(config_repository: FakeConfigRepository) -> None:
    view = FakePomodoroEditView()
    presenter = PomodoroEditPresenter(view, PomodoroService(config_repository), FakeSoundService())
    calls: list[None] = []
    presenter.bind_closed(lambda: calls.append(None))
    presenter.start_create()

    view.callbacks["close_clicked"]()

    assert len(calls) == 1


# EOF
