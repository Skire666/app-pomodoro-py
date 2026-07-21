from pomodoro.shared.errors.config_error import ErrorCodeConfig
from pomodoro.shared.errors.pomodoro_error import ErrorCodePomodoro
from pomodoro.shared.exceptions.repository_exception import ConfigReadError


def test_message_returns_the_french_text_carried_by_the_member() -> None:
    assert ErrorCodePomodoro.POM_1001.message == "Le nom est requis."


def test_try_simplify_exception_returns_none_by_default() -> None:
    assert ErrorCodePomodoro.try_simplify_exception(ValueError("boom")) is None


def test_try_simplify_exception_maps_a_known_repository_exception() -> None:
    mapped = ErrorCodeConfig.try_simplify_exception(ConfigReadError("boom"))

    assert mapped is ErrorCodeConfig.CFG_1001


def test_try_simplify_exception_returns_none_for_an_unrelated_exception() -> None:
    assert ErrorCodeConfig.try_simplify_exception(ValueError("boom")) is None


# EOF
