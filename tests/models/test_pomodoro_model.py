from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.shared.enums.copy_mode_enum import CopyModeEnum
from pomodoro.shared.errors.pomodoro_error import ErrorCodePomodoro


def test_validate_fails_when_name_is_empty() -> None:
    pomodoro = PomodoroModel.get_default()
    pomodoro.name = "   "
    pomodoro.duration_seconds = 60

    result = pomodoro.validate()

    assert result.is_valid is False
    assert result.error_code is ErrorCodePomodoro.POM_1001


def test_validate_fails_when_duration_is_zero() -> None:
    pomodoro = PomodoroModel.get_default()
    pomodoro.name = "Sprint deep work"
    pomodoro.duration_seconds = 0

    result = pomodoro.validate()

    assert result.is_valid is False
    assert result.error_code is ErrorCodePomodoro.POM_1002


def test_validate_succeeds_with_a_name_and_a_positive_duration() -> None:
    pomodoro = PomodoroModel.get_default()
    pomodoro.name = "Sprint deep work"

    result = pomodoro.validate()

    assert result.is_valid is True
    assert result.error_code is None


def test_to_dict_and_from_dict_round_trip_preserves_every_field() -> None:
    original = PomodoroModel.get_default()
    original.id_pomodoro = "pom-1"
    original.name = "Sprint deep work"
    original.duration_seconds = 1500
    original.sound_path = "son_cloche.mp3"
    original.sound_volume = 80
    original.sound_repeat_count = 3
    original.sound_repeat_interval_seconds = 10

    rebuilt = PomodoroModel.from_dict(original.to_dict())

    assert rebuilt.to_dict() == original.to_dict()


def test_copy_business_mode_clears_identity_but_keeps_settings() -> None:
    original = PomodoroModel.get_default()
    original.id_pomodoro = "pom-1"
    original.name = "Sprint deep work"
    original.duration_seconds = 1500

    clone = original.copy(CopyModeEnum.E_BUSINESS)

    assert clone.id_pomodoro == ""
    assert clone.name == "Sprint deep work"
    assert clone.duration_seconds == 1500
    assert clone is not original
    assert clone.sound is not original.sound


def test_copy_technical_mode_preserves_identity() -> None:
    original = PomodoroModel.get_default()
    original.id_pomodoro = "pom-1"

    clone = original.copy(CopyModeEnum.E_TECHNICAL)

    assert clone.id_pomodoro == "pom-1"
    assert clone is not original


def test_clear_resets_every_field_to_its_default_value() -> None:
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = "pom-1"
    pomodoro.name = "Sprint deep work"

    pomodoro.clear()

    assert pomodoro.id_pomodoro == ""
    assert pomodoro.name == ""


def test_mark_as_modified_updates_modified_at_but_not_created_at() -> None:
    pomodoro = PomodoroModel.get_default()
    created_at = pomodoro.created_at

    pomodoro.mark_as_modified()

    assert pomodoro.created_at == created_at
    assert pomodoro.modified_at >= created_at


# EOF
