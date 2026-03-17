from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from ..models import RawArticle, SourceHealth


@dataclass(slots=True)
class SourceConfig:
    key: str
    label: str
    start_urls: list[str]
    collection_mode: str
    kind: str
    max_items_per_run: int


@dataclass(slots=True)
class CollectorResult:
    items: list[RawArticle] = field(default_factory=list)
    health: SourceHealth | None = None


class Collector(Protocol):
    def collect(self, config: SourceConfig) -> CollectorResult:
        """Collect raw items for the configured source."""
