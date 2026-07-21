from datetime import UTC, datetime, timedelta

from pomodoro.models.active_session_model import ActiveSessionModel

_BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)


def _make_session(planned_duration_seconds: int = 1500) -> ActiveSessionModel:
    return ActiveSessionModel(
        id_pomodoro="pom-1",
        name_snapshot="Sprint deep work",
        planned_duration_seconds=planned_duration_seconds,
        accumulated_seconds=0,
        is_paused=False,
        last_resumed_at=_BASE_TIME,
        created_at=_BASE_TIME,
        modified_at=_BASE_TIME,
    )


def test_remaining_seconds_decreases_as_time_passes_while_running() -> None:
    session = _make_session(planned_duration_seconds=1500)

    remaining = session.remaining_seconds(_BASE_TIME + timedelta(seconds=100))

    assert remaining == 1400


def test_remaining_seconds_floors_at_zero_past_completion() -> None:
    session = _make_session(planned_duration_seconds=60)

    remaining = session.remaining_seconds(_BASE_TIME + timedelta(seconds=200))

    assert remaining == 0


def test_is_complete_becomes_true_once_the_planned_duration_elapses() -> None:
    session = _make_session(planned_duration_seconds=60)

    assert session.is_complete(_BASE_TIME + timedelta(seconds=30)) is False
    assert session.is_complete(_BASE_TIME + timedelta(seconds=60)) is True


def test_pause_freezes_the_countdown() -> None:
    session = _make_session(planned_duration_seconds=1500)
    pause_time = _BASE_TIME + timedelta(seconds=100)

    session.pause(pause_time)

    assert session.is_paused is True
    assert session.accumulated_seconds == 100
    assert session.remaining_seconds(pause_time + timedelta(seconds=500)) == 1400


def test_resume_continues_the_countdown_from_where_it_was_paused() -> None:
    session = _make_session(planned_duration_seconds=1500)
    session.pause(_BASE_TIME + timedelta(seconds=100))
    resume_time = _BASE_TIME + timedelta(seconds=300)

    session.resume(resume_time)

    assert session.is_paused is False
    assert session.remaining_seconds(resume_time + timedelta(seconds=50)) == 1350


def test_pause_while_already_paused_is_a_no_op() -> None:
    session = _make_session(planned_duration_seconds=1500)
    session.pause(_BASE_TIME + timedelta(seconds=100))

    session.pause(_BASE_TIME + timedelta(seconds=999))

    assert session.accumulated_seconds == 100


def test_resume_while_already_running_is_a_no_op() -> None:
    session = _make_session(planned_duration_seconds=1500)

    session.resume(_BASE_TIME + timedelta(seconds=999))

    assert session.last_resumed_at == _BASE_TIME


def test_to_dict_and_from_dict_round_trip_preserves_every_field() -> None:
    original = _make_session()
    original.pause(_BASE_TIME + timedelta(seconds=42))

    rebuilt = ActiveSessionModel.from_dict(original.to_dict())

    assert rebuilt.to_dict() == original.to_dict()


# EOF
