from datetime import UTC, datetime

from morning_radio.weekly_quantum.config import WeeklyQuantumConfig
from morning_radio.weekly_quantum.models import WeeklyRunState
from morning_radio.weekly_quantum.window import determine_collection_window


def test_bootstrap_window_uses_initial_lookback():
    now = datetime(2026, 3, 16, 0, 0, tzinfo=UTC)
    state = WeeklyRunState()
    config = WeeklyQuantumConfig(initial_lookback_days=8)
    window = determine_collection_window(now=now, state=state, config=config)
    assert window.bootstrap is True
    assert (window.end - window.start).days == 8


def test_existing_state_uses_last_successful_end():
    now = datetime(2026, 3, 16, 0, 0, tzinfo=UTC)
    state = WeeklyRunState(last_successful_window_end=datetime(2026, 3, 9, 0, 0, tzinfo=UTC))
    config = WeeklyQuantumConfig(initial_lookback_days=8)
    window = determine_collection_window(now=now, state=state, config=config)
    assert window.bootstrap is False
    assert window.start == datetime(2026, 3, 9, 0, 0, tzinfo=UTC)
    assert window.end == now
