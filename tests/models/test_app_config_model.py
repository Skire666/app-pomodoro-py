from pomodoro.models.app_config_model import AppConfigModel
from pomodoro.models.pomodoro_model import PomodoroModel


def test_instance_lazily_creates_a_default_singleton() -> None:
    AppConfigModel.set_instance(AppConfigModel.get_default())

    first = AppConfigModel.instance()
    second = AppConfigModel.instance()

    assert first is second


def test_set_instance_replaces_the_singleton() -> None:
    replacement = AppConfigModel.get_default()

    AppConfigModel.set_instance(replacement)

    assert AppConfigModel.instance() is replacement


def test_to_dict_and_from_dict_round_trip_preserves_the_pomodoro_collection() -> None:
    config = AppConfigModel.get_default()
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = "pom-1"
    pomodoro.name = "Sprint deep work"
    config.pomodoros.create(pomodoro)

    rebuilt = AppConfigModel.from_dict(config.to_dict())

    assert rebuilt.pomodoros.read("pom-1") is not None


def test_validate_fails_when_a_nested_pomodoro_is_invalid() -> None:
    config = AppConfigModel.get_default()
    config.pomodoros.create(PomodoroModel.get_default())

    assert config.validate().is_valid is False


# EOF
