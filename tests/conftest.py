import pytest

from pomodoro.models.app_config_model import AppConfigModel


class FakeConfigRepository:
    def __init__(self) -> None:
        self.save_count = 0

    def load(self) -> AppConfigModel:
        return AppConfigModel.get_default()

    def save(self, config: AppConfigModel) -> None:
        self.save_count += 1

    def invalidate_cache(self) -> None:
        pass


@pytest.fixture
def config_repository() -> FakeConfigRepository:
    return FakeConfigRepository()


@pytest.fixture(autouse=True)
def _reset_app_config_singleton() -> None:
    AppConfigModel.set_instance(AppConfigModel.get_default())


# EOF
