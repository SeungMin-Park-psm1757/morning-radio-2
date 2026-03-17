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
    manual_override: bool = False


def determine_collection_window(
    *,
    now: datetime,
    state: WeeklyRunState,
    config: WeeklyQuantumConfig,
) -> CollectionWindow:
    now_utc = now.astimezone(UTC)
    manual_start = config.window_start_override.astimezone(UTC) if config.window_start_override else None
    manual_end = config.window_end_override.astimezone(UTC) if config.window_end_override else None

    if manual_start is not None or manual_end is not None:
        end = manual_end or now_utc
        if manual_start is not None:
            start = manual_start
            bootstrap = False
        elif state.last_successful_window_end is not None:
            start = state.last_successful_window_end.astimezone(UTC)
            bootstrap = False
        else:
            start = end - timedelta(days=config.initial_lookback_days)
            bootstrap = True
        if start >= end:
            raise ValueError("Collection window start must be earlier than window end.")
        return CollectionWindow(start=start, end=end, bootstrap=bootstrap, manual_override=True)

    if state.last_successful_window_end is None:
        return CollectionWindow(
            start=now_utc - timedelta(days=config.initial_lookback_days),
            end=now_utc,
            bootstrap=True,
            manual_override=False,
        )

    return CollectionWindow(
        start=state.last_successful_window_end.astimezone(UTC),
        end=now_utc,
        bootstrap=False,
        manual_override=False,
    )
