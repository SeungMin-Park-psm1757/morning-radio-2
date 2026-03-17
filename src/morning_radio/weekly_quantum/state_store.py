from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .models import WeeklyRunState


def load_run_state(path: Path) -> WeeklyRunState:
    if not path.exists():
        return WeeklyRunState()

    data = json.loads(path.read_text(encoding="utf-8"))
    return WeeklyRunState(
        last_attempt_started_at=_parse_dt(data.get("last_attempt_started_at")),
        last_successful_window_end=_parse_dt(data.get("last_successful_window_end")),
        last_successful_run_dir=data.get("last_successful_run_dir"),
        last_delivery_status=data.get("last_delivery_status"),
        last_source_health=data.get("last_source_health", []),
    )


def save_run_state(path: Path, state: WeeklyRunState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(state)
    for key in ("last_attempt_started_at", "last_successful_window_end"):
        value = payload.get(key)
        if isinstance(value, datetime):
            payload[key] = value.isoformat()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)
