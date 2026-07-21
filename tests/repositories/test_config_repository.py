from pathlib import Path

import pytest

from pomodoro.models.app_config_model import AppConfigModel
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.repositories.config_repository import ConfigRepository
from pomodoro.shared.exceptions.repository_exception import ConfigCorruptedError


def test_load_returns_a_default_configuration_when_the_file_is_missing(tmp_path: Path) -> None:
    repository = ConfigRepository(tmp_path / "config-pomodoro.json")

    config = repository.load()

    assert len(config.pomodoros) == 0


def test_save_then_load_round_trips_the_configuration(tmp_path: Path) -> None:
    config_path = tmp_path / "config-pomodoro.json"
    repository = ConfigRepository(config_path)
    config = AppConfigModel.get_default()
    pomodoro = PomodoroModel.get_default()
    pomodoro.id_pomodoro = "pom-1"
    pomodoro.name = "Sprint deep work"
    config.pomodoros.create(pomodoro)

    repository.save(config)
    repository.invalidate_cache()
    reloaded = repository.load()

    assert reloaded.pomodoros.read("pom-1") is not None
    assert config_path.exists()
    assert not config_path.with_name(config_path.name + ".tmp").exists()


def test_save_does_not_leave_a_tmp_file_behind(tmp_path: Path) -> None:
    config_path = tmp_path / "config-pomodoro.json"
    repository = ConfigRepository(config_path)

    repository.save(AppConfigModel.get_default())

    assert list(tmp_path.iterdir()) == [config_path]


def test_load_caches_the_configuration_until_invalidated(tmp_path: Path) -> None:
    config_path = tmp_path / "config-pomodoro.json"
    repository = ConfigRepository(config_path)
    repository.save(AppConfigModel.get_default())

    first = repository.load()
    second = repository.load()

    assert first is second

    repository.invalidate_cache()
    third = repository.load()

    assert third is not first


def test_load_raises_config_corrupted_error_when_json_is_invalid(tmp_path: Path) -> None:
    config_path = tmp_path / "config-pomodoro.json"
    config_path.write_text("{not valid json", encoding="utf-8")
    repository = ConfigRepository(config_path)

    with pytest.raises(ConfigCorruptedError):
        repository.load()


# EOF
