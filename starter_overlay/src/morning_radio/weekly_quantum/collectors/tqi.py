from __future__ import annotations

from .base import CollectorResult, SourceConfig
from ..models import SourceHealth


class TQICollector:
    """Starter collector stub for The Quantum Insider."""

    def collect(self, config: SourceConfig) -> CollectorResult:
        health = SourceHealth(
            source_key=config.key,
            requested=True,
            success=False,
            fallback_mode_used="not_implemented",
            error="Collector stub only. Replace with real implementation.",
        )
        return CollectorResult(items=[], health=health)
