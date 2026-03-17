from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from .config import WeeklyQuantumConfig
from .models import WeeklyRunState


@dataclass(slots=True)
class CollectionWindow:
    start: datetime
    end: datetime
    bootstrap: bool = False


def determine_collection_window(
    *,
    now: datetime,
    state: WeeklyRunState,
    config: WeeklyQuantumConfig,
) -> CollectionWindow:
    now_utc = now.astimezone(UTC)

    if state.last_successful_window_end is None:
        return CollectionWindow(
            start=now_utc - timedelta(days=config.initial_lookback_days),
            end=now_utc,
            bootstrap=True,
        )

    return CollectionWindow(
        start=state.last_successful_window_end.astimezone(UTC),
        end=now_utc,
        bootstrap=False,
    )
