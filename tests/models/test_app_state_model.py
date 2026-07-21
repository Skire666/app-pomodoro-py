from pomodoro.models.app_state_model import AppStateModel


def test_is_busy_stays_true_until_every_holder_releases_it() -> None:
    state = AppStateModel()

    state.set_busy("view-a", True)
    state.set_busy("view-b", True)
    state.set_busy("view-a", False)

    assert state.is_busy is True

    state.set_busy("view-b", False)

    assert state.is_busy is False


def test_releasing_a_holder_that_never_asserted_is_a_no_op() -> None:
    state = AppStateModel()

    state.set_dirty("view-a", False)

    assert state.is_dirty is False


def test_clear_releases_every_holder_and_resets_the_active_view() -> None:
    state = AppStateModel()
    state.set_busy("view-a", True)
    state.set_loading("view-a", True)
    state.set_dirty("view-a", True)

    state.clear()

    assert state.is_busy is False
    assert state.is_loading is False
    assert state.is_dirty is False


# EOF
