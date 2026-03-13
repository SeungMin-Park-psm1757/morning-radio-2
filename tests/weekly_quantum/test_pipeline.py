from datetime import UTC, datetime
from pathlib import Path

from morning_radio.weekly_quantum.pipeline import run_weekly_quantum_pipeline
from morning_radio.weekly_quantum.state_store import load_run_state

from .conftest import make_config


def test_pipeline_writes_weekly_outputs_and_does_not_advance_success_state(tmp_path: Path):
    now = datetime(2026, 3, 16, 0, 0, tzinfo=UTC)
    config = make_config(
        output_dir=tmp_path / "output" / "weekly_quantum",
        state_path=tmp_path / "state" / "weekly_quantum_run_state.json",
        skip_llm=True,
        skip_tts=True,
        skip_telegram=True,
        dry_run=True,
    )

    run_dir = run_weekly_quantum_pipeline(config, now=now)

    expected_files = {
        "raw_items.json",
        "normalized_items.json",
        "clusters.json",
        "selected_items.json",
        "category_briefs.json",
        "weekly_show.json",
        "weekly_script.md",
        "weekly_script.txt",
        "weekly_headlines.txt",
        "message_digest.md",
        "source_health.json",
        "summary.md",
        "run_metadata.json",
    }
    assert expected_files <= {path.name for path in run_dir.iterdir()}

    state = load_run_state(config.state_path)
    assert state.last_attempt_started_at == now
    assert state.last_successful_window_end is None
