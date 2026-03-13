from __future__ import annotations

from pathlib import Path

from morning_radio.weekly_quantum.config import WeeklyQuantumConfig


def make_config(**overrides: object) -> WeeklyQuantumConfig:
    config = WeeklyQuantumConfig(
        timezone_name="Asia/Seoul",
        output_dir=Path("output/weekly_quantum"),
        state_path=Path("state/weekly_quantum_run_state.json"),
        initial_lookback_days=8,
        max_list_items_per_source=80,
        max_detail_fetches=16,
        max_selected_stories=12,
        budget_mode="low",
        request_timeout_seconds=20,
        retry_count=2,
        enable_tts=True,
        enable_telegram=True,
        skip_llm=True,
        skip_tts=True,
        skip_telegram=True,
        dry_run=True,
        host_name="민준",
        analyst_name="서연",
    )
    for key, value in overrides.items():
        setattr(config, key, value)
    return config
