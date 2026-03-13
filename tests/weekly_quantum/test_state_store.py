from datetime import UTC, datetime
from pathlib import Path

from morning_radio.weekly_quantum.models import WeeklyRunState
from morning_radio.weekly_quantum.state_store import load_run_state, save_run_state


def test_roundtrip_state(tmp_path: Path):
    path = tmp_path / "state.json"
    state = WeeklyRunState(
        last_attempt_started_at=datetime(2026, 3, 16, 0, 0, tzinfo=UTC),
        last_successful_window_end=datetime(2026, 3, 16, 0, 0, tzinfo=UTC),
        last_successful_run_dir="output/weekly_quantum/20260316-000000",
        last_delivery_status="ok",
    )
    save_run_state(path, state)
    loaded = load_run_state(path)
    assert loaded.last_delivery_status == "ok"
    assert loaded.last_successful_run_dir.endswith("20260316-000000")
