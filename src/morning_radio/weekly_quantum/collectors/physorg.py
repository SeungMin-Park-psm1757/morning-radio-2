from __future__ import annotations

import time

from .base import BaseCollector, CollectorResult, SourceConfig

PHYSORG_RSS_URL = "https://phys.org/rss-feed/physics-news/quantum-physics/"


class PhysOrgCollector(BaseCollector):
    def collect(self, config: SourceConfig) -> CollectorResult:
        started_at = time.perf_counter()
        try:
            parsed_feed, status_code = self.fetch_feed(PHYSORG_RSS_URL)
            items = [
                article
                for entry in parsed_feed.entries[: config.max_items_per_run]
                if (article := self.feed_entry_to_article(entry, config=config, source_url=PHYSORG_RSS_URL))
            ]
            health = self.build_health(
                source_key=config.key,
                started_at=started_at,
                success=True,
                items_seen=len(items),
                http_status=status_code,
                fallback_mode_used="rss",
            )
            return CollectorResult(items=items, health=health)
        except Exception as exc:
            health = self.build_health(
                source_key=config.key,
                started_at=started_at,
                success=False,
                fallback_mode_used="rss_failed",
                error=str(exc),
            )
            return CollectorResult(items=[], health=health)
