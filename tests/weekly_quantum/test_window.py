from datetime import UTC, datetime

from morning_radio.weekly_quantum.models import WeeklyRunState
from morning_radio.weekly_quantum.window import determine_collection_window

from .conftest import make_config


def test_bootstrap_window_uses_initial_lookback():
    now = datetime(2026, 3, 16, 0, 0, tzinfo=UTC)
    state = WeeklyRunState()
    config = make_config(initial_lookback_days=8)
    window = determine_collection_window(now=now, state=state, config=config)
    assert window.bootstrap is True
    assert window.manual_override is False
    assert (window.end - window.start).days == 8


def test_existing_state_uses_last_successful_end():
    now = datetime(2026, 3, 16, 0, 0, tzinfo=UTC)
    state = WeeklyRunState(last_successful_window_end=datetime(2026, 3, 9, 0, 0, tzinfo=UTC))
    config = make_config(initial_lookback_days=8)
    window = determine_collection_window(now=now, state=state, config=config)
    assert window.bootstrap is False
    assert window.manual_override is False
    assert window.start == datetime(2026, 3, 9, 0, 0, tzinfo=UTC)
    assert window.end == now


def test_manual_window_override_wins():
    now = datetime(2026, 3, 16, 0, 0, tzinfo=UTC)
    state = WeeklyRunState(last_successful_window_end=datetime(2026, 3, 9, 0, 0, tzinfo=UTC))
    config = make_config(
        window_start_override=datetime(2026, 3, 1, 0, 0, tzinfo=UTC),
        window_end_override=datetime(2026, 3, 8, 0, 0, tzinfo=UTC),
    )
    window = determine_collection_window(now=now, state=state, config=config)
    assert window.manual_override is True
    assert window.start == datetime(2026, 3, 1, 0, 0, tzinfo=UTC)
    assert window.end == datetime(2026, 3, 8, 0, 0, tzinfo=UTC)


def test_manual_end_only_preserves_safe_catch_up():
    now = datetime(2026, 3, 16, 0, 0, tzinfo=UTC)
    state = WeeklyRunState(last_successful_window_end=datetime(2026, 3, 9, 0, 0, tzinfo=UTC))
    config = make_config(window_end_override=datetime(2026, 3, 12, 0, 0, tzinfo=UTC))
    window = determine_collection_window(now=now, state=state, config=config)
    assert window.manual_override is True
    assert window.start == datetime(2026, 3, 9, 0, 0, tzinfo=UTC)
    assert window.end == datetime(2026, 3, 12, 0, 0, tzinfo=UTC)
