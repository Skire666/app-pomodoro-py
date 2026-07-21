from pomodoro.shared.errors.pomodoro_error import ErrorCodePomodoro
from pomodoro.shared.validation_result import ValidationResult


def test_ok_builds_a_successful_result_without_error_code() -> None:
    result = ValidationResult.ok()

    assert result.is_valid is True
    assert result.error_code is None
    assert result.field_name is None


def test_error_builds_a_failed_result_carrying_the_error_code_and_field() -> None:
    result = ValidationResult.error(ErrorCodePomodoro.POM_1001, field_name="name")

    assert result.is_valid is False
    assert result.error_code is ErrorCodePomodoro.POM_1001
    assert result.field_name == "name"


def test_error_defaults_field_name_to_none_when_not_provided() -> None:
    result = ValidationResult.error(ErrorCodePomodoro.POM_1002)

    assert result.field_name is None


# EOF
