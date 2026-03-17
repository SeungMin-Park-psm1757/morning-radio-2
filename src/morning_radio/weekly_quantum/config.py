from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .collectors.base import SourceConfig

_SOURCE_SPECS: tuple[tuple[str, str, str, str, int], ...] = (
    ("tqi_daily", "The Quantum Insider Daily", "https://thequantuminsider.com/category/daily/", "tqi", 40),
    (
        "tqi_national",
        "The Quantum Insider National",
        "https://thequantuminsider.com/category/daily/national/",
        "tqi",
        20,
    ),
    (
        "tqi_business",
        "The Quantum Insider Business",
        "https://thequantuminsider.com/category/daily/business/",
        "tqi",
        20,
    ),
    (
        "tqi_research",
        "The Quantum Insider Research and Tech",
        "https://thequantuminsider.com/category/daily/researchandtech/",
        "tqi",
        20,
    ),
    (
        "tqi_education",
        "The Quantum Insider Education",
        "https://thequantuminsider.com/category/exclusives/education/",
        "tqi",
        8,
    ),
    (
        "tqi_insights",
        "The Quantum Insider Insights",
        "https://thequantuminsider.com/category/exclusives/insights/",
        "tqi",
        8,
    ),
    (
        "physorg_quantum",
        "Phys.org Quantum Physics",
        "https://phys.org/physics-news/quantum-physics/?hl=ko-KR",
        "physorg",
        30,
    ),
    (
        "quantumzeitgeist_research",
        "Quantum Zeitgeist Research News",
        "https://quantumzeitgeist.com/category/quantum-research-news/",
        "quantumzeitgeist",
        25,
    ),
    (
        "qcr_news",
        "Quantum Computing Report News",
        "https://quantumcomputingreport.com/news/",
        "qcr",
        25,
    ),
    (
        "qcr_our_take",
        "Quantum Computing Report Our Take",
        "https://quantumcomputingreport.com/our-take/",
        "qcr",
        10,
    ),
    (
        "qcr_qnalysis",
        "Quantum Computing Report Qnalysis",
        "https://quantumcomputingreport.com/qnalysis/",
        "qcr",
        8,
    ),
    (
        "quantumfrontiers_news",
        "Quantum Frontiers News",
        "https://quantumfrontiers.com/category/news/",
        "quantumfrontiers",
        10,
    ),
)


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _parse_datetime(value: str | None, timezone: ZoneInfo) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone)
    return parsed


@dataclass(slots=True)
class WeeklyQuantumConfig:
    timezone_name: str
    output_dir: Path
    state_path: Path
    initial_lookback_days: int
    max_list_items_per_source: int
    max_detail_fetches: int
    max_selected_stories: int
    budget_mode: str
    request_timeout_seconds: int
    retry_count: int
    editor_model: str
    triage_model: str
    tts_model: str
    max_output_tokens: int
    enable_tts: bool
    enable_telegram: bool
    skip_llm: bool
    skip_tts: bool
    skip_telegram: bool
    dry_run: bool
    host_name: str
    analyst_name: str
    host_voice: str
    analyst_voice: str
    tts_speed_multiplier: float
    tts_turn_pause_multiplier: float
    tts_retry_count: int
    tts_retry_delay_seconds: int
    gemini_api_key: str | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    telegram_thread_id: str | None = None
    telegram_silent: bool = False
    public_archive_base_url: str | None = None
    window_start_override: datetime | None = None
    window_end_override: datetime | None = None

    @property
    def timezone(self) -> ZoneInfo:
        return ZoneInfo(self.timezone_name)

    @property
    def llm_enabled(self) -> bool:
        return bool(self.gemini_api_key) and not self.skip_llm

    @property
    def tts_enabled(self) -> bool:
        return self.llm_enabled and self.enable_tts and not self.skip_tts

    @property
    def telegram_enabled(self) -> bool:
        return (
            bool(self.telegram_bot_token and self.telegram_chat_id)
            and self.enable_telegram
            and not self.skip_telegram
            and not self.dry_run
        )

    @property
    def tts_bitrate_kbps(self) -> int:
        return 48

    @property
    def llm_story_limit(self) -> int:
        if self.budget_mode == "safe":
            return min(self.max_selected_stories, 8)
        if self.budget_mode == "standard":
            return min(self.max_selected_stories, 12)
        return min(self.max_selected_stories, 10)

    def to_safe_dict(self) -> dict[str, object]:
        return {
            "timezone_name": self.timezone_name,
            "output_dir": str(self.output_dir),
            "state_path": str(self.state_path),
            "initial_lookback_days": self.initial_lookback_days,
            "max_list_items_per_source": self.max_list_items_per_source,
            "max_detail_fetches": self.max_detail_fetches,
            "max_selected_stories": self.max_selected_stories,
            "budget_mode": self.budget_mode,
            "request_timeout_seconds": self.request_timeout_seconds,
            "retry_count": self.retry_count,
            "editor_model": self.editor_model,
            "triage_model": self.triage_model,
            "tts_model": self.tts_model,
            "max_output_tokens": self.max_output_tokens,
            "enable_tts": self.enable_tts,
            "enable_telegram": self.enable_telegram,
            "skip_llm": self.skip_llm,
            "skip_tts": self.skip_tts,
            "skip_telegram": self.skip_telegram,
            "dry_run": self.dry_run,
            "host_name": self.host_name,
            "analyst_name": self.analyst_name,
            "host_voice": self.host_voice,
            "analyst_voice": self.analyst_voice,
            "tts_speed_multiplier": self.tts_speed_multiplier,
            "tts_turn_pause_multiplier": self.tts_turn_pause_multiplier,
            "tts_retry_count": self.tts_retry_count,
            "tts_retry_delay_seconds": self.tts_retry_delay_seconds,
            "window_start_override": self.window_start_override.isoformat()
            if self.window_start_override
            else None,
            "window_end_override": self.window_end_override.isoformat()
            if self.window_end_override
            else None,
            "source_count": len(build_source_configs(self.max_list_items_per_source)),
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the weekly quantum-only morning-radio package.",
    )
    parser.add_argument(
        "--output-dir",
        default=os.getenv("WEEKLY_QUANTUM_OUTPUT_DIR", "output/weekly_quantum"),
        help="Directory where weekly artifacts will be written.",
    )
    parser.add_argument(
        "--state-path",
        default=os.getenv("WEEKLY_QUANTUM_STATE_PATH", "state/weekly_quantum_run_state.json"),
        help="Path to the weekly run-state file.",
    )
    parser.add_argument(
        "--window-start",
        help="Optional ISO-8601 override for the collection window start.",
    )
    parser.add_argument(
        "--window-end",
        help="Optional ISO-8601 override for the collection window end.",
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip LLM steps and use heuristic brief generation.",
    )
    parser.add_argument(
        "--skip-tts",
        action="store_true",
        help="Skip TTS generation even if enabled in the environment.",
    )
    parser.add_argument(
        "--skip-telegram",
        action="store_true",
        help="Skip Telegram delivery.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build outputs without Telegram delivery.",
    )
    return parser


def build_source_configs(max_items_per_source: int) -> list[SourceConfig]:
    configs = [
        SourceConfig(
            key=key,
            label=label,
            start_urls=[start_url],
            collection_mode="direct",
            kind=kind,
            max_items_per_run=min(default_cap, max_items_per_source),
        )
        for key, label, start_url, kind, default_cap in _SOURCE_SPECS
    ]
    validate_source_configs(configs)
    return configs


def validate_source_configs(configs: list[SourceConfig]) -> None:
    seen_keys: set[str] = set()
    seen_urls: set[str] = set()
    for config in configs:
        if not config.key:
            raise ValueError("Source config key must not be empty.")
        if config.key in seen_keys:
            raise ValueError(f"Duplicate source key: {config.key}")
        seen_keys.add(config.key)

        if config.max_items_per_run <= 0:
            raise ValueError(f"Source config {config.key} must have a positive max_items_per_run.")
        if not config.start_urls:
            raise ValueError(f"Source config {config.key} must define at least one start URL.")

        for url in config.start_urls:
            normalized = url.rstrip("/")
            if normalized in seen_urls:
                raise ValueError(f"Duplicate source URL: {url}")
            seen_urls.add(normalized)


def load_weekly_quantum_config(args: argparse.Namespace | None = None) -> WeeklyQuantumConfig:
    _load_dotenv(Path(".env"))
    if args is None:
        args = build_parser().parse_args([])

    timezone_name = os.getenv("WEEKLY_QUANTUM_TIMEZONE", "Asia/Seoul")
    timezone = ZoneInfo(timezone_name)
    config = WeeklyQuantumConfig(
        timezone_name=timezone_name,
        output_dir=Path(args.output_dir),
        state_path=Path(args.state_path),
        initial_lookback_days=int(os.getenv("WEEKLY_QUANTUM_INITIAL_LOOKBACK_DAYS", "8")),
        max_list_items_per_source=int(os.getenv("WEEKLY_QUANTUM_MAX_LIST_ITEMS_PER_SOURCE", "80")),
        max_detail_fetches=int(os.getenv("WEEKLY_QUANTUM_MAX_DETAIL_FETCHES", "16")),
        max_selected_stories=int(os.getenv("WEEKLY_QUANTUM_MAX_SELECTED_STORIES", "12")),
        budget_mode=os.getenv("WEEKLY_QUANTUM_BUDGET_MODE", "low"),
        request_timeout_seconds=int(os.getenv("WEEKLY_QUANTUM_REQUEST_TIMEOUT_SECONDS", "20")),
        retry_count=int(os.getenv("WEEKLY_QUANTUM_RETRY_COUNT", "2")),
        editor_model=os.getenv("WEEKLY_QUANTUM_EDITOR_MODEL", "gemini-2.5-flash"),
        triage_model=os.getenv("WEEKLY_QUANTUM_TRIAGE_MODEL", "gemini-2.5-flash-lite"),
        tts_model=os.getenv("WEEKLY_QUANTUM_TTS_MODEL", "gemini-2.5-flash-preview-tts"),
        max_output_tokens=int(os.getenv("WEEKLY_QUANTUM_MAX_OUTPUT_TOKENS", "4096")),
        enable_tts=_get_bool("WEEKLY_QUANTUM_ENABLE_TTS", True),
        enable_telegram=_get_bool("WEEKLY_QUANTUM_ENABLE_TELEGRAM", True),
        skip_llm=args.skip_llm,
        skip_tts=args.skip_tts,
        skip_telegram=args.skip_telegram,
        dry_run=args.dry_run,
        host_name=os.getenv("WEEKLY_QUANTUM_HOST_NAME", "민준"),
        analyst_name=os.getenv("WEEKLY_QUANTUM_ANALYST_NAME", "서연"),
        host_voice=os.getenv("WEEKLY_QUANTUM_HOST_VOICE", "Charon"),
        analyst_voice=os.getenv("WEEKLY_QUANTUM_ANALYST_VOICE", "Leda"),
        tts_speed_multiplier=float(os.getenv("WEEKLY_QUANTUM_TTS_SPEED", "1.0")),
        tts_turn_pause_multiplier=float(os.getenv("WEEKLY_QUANTUM_TTS_TURN_PAUSE", "1.0")),
        tts_retry_count=int(os.getenv("WEEKLY_QUANTUM_TTS_RETRY_COUNT", "1")),
        tts_retry_delay_seconds=int(os.getenv("WEEKLY_QUANTUM_TTS_RETRY_DELAY_SECONDS", "40")),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        telegram_thread_id=os.getenv("TELEGRAM_THREAD_ID"),
        telegram_silent=_get_bool("WEEKLY_QUANTUM_TELEGRAM_SILENT", False),
        public_archive_base_url=os.getenv("WEEKLY_QUANTUM_PUBLIC_ARCHIVE_BASE_URL"),
        window_start_override=_parse_datetime(args.window_start, timezone),
        window_end_override=_parse_datetime(args.window_end, timezone),
    )
    build_source_configs(config.max_list_items_per_source)
    return config
