from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from dateutil.tz import tzoffset

from ..models import RawArticle, SourceHealth

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)
TZINFOS = {
    "EDT": tzoffset("EDT", -4 * 3600),
    "EST": tzoffset("EST", -5 * 3600),
}


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


class BaseCollector:
    def __init__(self, *, timeout_seconds: int = 20, retry_count: int = 2) -> None:
        self.timeout_seconds = timeout_seconds
        self.retry_count = retry_count
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

    def fetch_text(self, url: str) -> tuple[str, int]:
        last_error: Exception | None = None
        for attempt in range(self.retry_count + 1):
            try:
                response = self.session.get(url, timeout=self.timeout_seconds)
                response.raise_for_status()
                apparent = getattr(response, "apparent_encoding", None)
                if apparent and (not response.encoding or response.encoding.lower() == "iso-8859-1"):
                    response.encoding = apparent
                return response.text, response.status_code
            except requests.RequestException as exc:
                last_error = exc
                if attempt >= self.retry_count:
                    raise
        raise RuntimeError(f"Failed to fetch {url}: {last_error}")

    def fetch_feed(self, url: str) -> tuple[feedparser.FeedParserDict, int]:
        text, status_code = self.fetch_text(url)
        return feedparser.parse(text), status_code

    def build_health(
        self,
        *,
        source_key: str,
        started_at: float,
        success: bool,
        items_seen: int = 0,
        http_status: int | None = None,
        fallback_mode_used: str | None = None,
        error: str | None = None,
    ) -> SourceHealth:
        return SourceHealth(
            source_key=source_key,
            requested=True,
            success=success,
            http_status=http_status,
            items_seen=items_seen,
            items_in_window=items_seen,
            fallback_mode_used=fallback_mode_used,
            error=error,
            latency_ms=int((time.perf_counter() - started_at) * 1000),
        )

    def html_to_text(self, value: str | None) -> str:
        if not value:
            return ""
        return BeautifulSoup(value, "html.parser").get_text(" ", strip=True)

    def parse_datetime(self, value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            parsed = date_parser.parse(value, tzinfos=TZINFOS)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=UTC)
            return parsed.astimezone(UTC)
        except (ValueError, TypeError, OverflowError):
            return None

    def build_raw_article(
        self,
        *,
        config: SourceConfig,
        title: str,
        canonical_url: str,
        source_url: str,
        published_at: datetime | None,
        excerpt: str = "",
        author: str | None = None,
        collection_method: str,
        tags: list[str] | None = None,
    ) -> RawArticle:
        return RawArticle(
            source_key=config.key,
            source_label=config.label,
            source_url=source_url,
            section_key=config.key,
            title=title.strip(),
            canonical_url=canonical_url.strip(),
            published_at=published_at,
            author=author.strip() if author else None,
            excerpt=excerpt.strip(),
            tags=tags or [],
            collection_method=collection_method,
        )

    def feed_entry_to_article(
        self,
        entry: feedparser.FeedParserDict,
        *,
        config: SourceConfig,
        source_url: str,
    ) -> RawArticle | None:
        title = self.html_to_text(entry.get("title"))
        link = entry.get("link")
        if not title or not link:
            return None
        summary = self.html_to_text(entry.get("summary") or entry.get("description"))
        author = self.html_to_text(entry.get("author"))
        tags = [tag.get("term", "").strip() for tag in entry.get("tags", []) if tag.get("term")]
        published_at = self.parse_datetime(entry.get("published") or entry.get("updated"))
        return self.build_raw_article(
            config=config,
            title=title,
            canonical_url=link,
            source_url=source_url,
            published_at=published_at,
            excerpt=summary,
            author=author or None,
            collection_method="rss",
            tags=tags,
        )

    def category_feed_url(self, start_url: str) -> str:
        return urljoin(start_url.rstrip("/") + "/", "feed/")
