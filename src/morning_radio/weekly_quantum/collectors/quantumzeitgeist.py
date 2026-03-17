from __future__ import annotations

import time

from bs4 import BeautifulSoup

from .base import BaseCollector, CollectorResult, SourceConfig


class QuantumZeitgeistCollector(BaseCollector):
    def collect(self, config: SourceConfig) -> CollectorResult:
        started_at = time.perf_counter()
        feed_url = self.category_feed_url(config.start_urls[0])
        try:
            parsed_feed, status_code = self.fetch_feed(feed_url)
            items = [
                article
                for entry in parsed_feed.entries[: config.max_items_per_run]
                if (article := self.feed_entry_to_article(entry, config=config, source_url=feed_url))
            ]
            if items:
                health = self.build_health(
                    source_key=config.key,
                    started_at=started_at,
                    success=True,
                    items_seen=len(items),
                    http_status=status_code,
                    fallback_mode_used="rss",
                )
                return CollectorResult(items=items, health=health)
        except Exception:
            pass

        try:
            html, status_code = self.fetch_text(config.start_urls[0])
            items = self._parse_html_list(html, config)
            health = self.build_health(
                source_key=config.key,
                started_at=started_at,
                success=True,
                items_seen=len(items),
                http_status=status_code,
                fallback_mode_used="html_list",
            )
            return CollectorResult(items=items, health=health)
        except Exception as exc:
            health = self.build_health(
                source_key=config.key,
                started_at=started_at,
                success=False,
                fallback_mode_used="html_list_failed",
                error=str(exc),
            )
            return CollectorResult(items=[], health=health)

    def _parse_html_list(self, html: str, config: SourceConfig) -> list:
        soup = BeautifulSoup(html, "html.parser")
        items = []
        for article in soup.select("li.post")[: config.max_items_per_run]:
            link = article.select_one("h3.entry-title a")
            date_node = article.select_one(".entry-meta span:last-child")
            author_node = article.select_one(".author.vcard a")
            if link is None:
                continue
            items.append(
                self.build_raw_article(
                    config=config,
                    title=link.get_text(" ", strip=True),
                    canonical_url=link.get("href", ""),
                    source_url=config.start_urls[0],
                    published_at=self.parse_datetime(date_node.get_text(" ", strip=True) if date_node else None),
                    author=author_node.get_text(" ", strip=True) if author_node else None,
                    collection_method="html_list",
                )
            )
        return items
