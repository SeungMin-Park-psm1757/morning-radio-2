from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class WeeklyQuantumConfig:
    timezone: str = "Asia/Seoul"
    output_dir: Path = Path("output/weekly_quantum")
    state_path: Path = Path("state/weekly_quantum_run_state.json")
    site_config_path: Path = Path("config/sites.yaml")
    initial_lookback_days: int = 8
    max_list_items_per_source: int = 80
    max_detail_fetches: int = 16
    max_selected_stories: int = 12
    budget_mode: str = "low"
    enable_tts: bool = True
    enable_telegram: bool = True
    request_timeout_seconds: int = 20
    retry_count: int = 2
    host_name: str = "민준"
    analyst_name: str = "서연"


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_weekly_quantum_config() -> WeeklyQuantumConfig:
    return WeeklyQuantumConfig(
        timezone=os.getenv("WEEKLY_QUANTUM_TIMEZONE", "Asia/Seoul"),
        output_dir=Path(os.getenv("WEEKLY_QUANTUM_OUTPUT_DIR", "output/weekly_quantum")),
        state_path=Path(os.getenv("WEEKLY_QUANTUM_STATE_PATH", "state/weekly_quantum_run_state.json")),
        site_config_path=Path(os.getenv("WEEKLY_QUANTUM_SITE_CONFIG", "config/sites.yaml")),
        initial_lookback_days=int(os.getenv("WEEKLY_QUANTUM_INITIAL_LOOKBACK_DAYS", "8")),
        max_list_items_per_source=int(os.getenv("WEEKLY_QUANTUM_MAX_LIST_ITEMS_PER_SOURCE", "80")),
        max_detail_fetches=int(os.getenv("WEEKLY_QUANTUM_MAX_DETAIL_FETCHES", "16")),
        max_selected_stories=int(os.getenv("WEEKLY_QUANTUM_MAX_SELECTED_STORIES", "12")),
        budget_mode=os.getenv("WEEKLY_QUANTUM_BUDGET_MODE", "low"),
        enable_tts=_get_bool("WEEKLY_QUANTUM_ENABLE_TTS", True),
        enable_telegram=_get_bool("WEEKLY_QUANTUM_ENABLE_TELEGRAM", True),
        request_timeout_seconds=int(os.getenv("WEEKLY_QUANTUM_REQUEST_TIMEOUT_SECONDS", "20")),
        retry_count=int(os.getenv("WEEKLY_QUANTUM_RETRY_COUNT", "2")),
        host_name=os.getenv("WEEKLY_QUANTUM_HOST_NAME", "민준"),
        analyst_name=os.getenv("WEEKLY_QUANTUM_ANALYST_NAME", "서연"),
    )
