from __future__ import annotations

import re
import time

from bs4 import BeautifulSoup

from .base import BaseCollector, CollectorResult, SourceConfig

_QCR_DATE_RE = re.compile(r"^[A-Z][a-z]+ \d{1,2}, \d{4}$")


class QCRCollector(BaseCollector):
    def collect(self, config: SourceConfig) -> CollectorResult:
        started_at = time.perf_counter()
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
        for paragraph in soup.select(".post-content p"):
            date_tag = paragraph.find("strong")
            if date_tag is None:
                continue
            date_text = date_tag.get_text(" ", strip=True)
            if not _QCR_DATE_RE.match(date_text):
                continue

            link = paragraph.find("a", href=True)
            if link is None:
                continue

            title = link.get_text(" ", strip=True)
            text = paragraph.get_text(" ", strip=True)
            summary = text.replace(date_text, "", 1).strip()
            summary = summary.replace(title, "", 1).strip(" .")
            summary = re.sub(r"Read more in our full article here\.?", "", summary, flags=re.IGNORECASE).strip(" .")

            items.append(
                self.build_raw_article(
                    config=config,
                    title=title,
                    canonical_url=link.get("href", ""),
                    source_url=config.start_urls[0],
                    published_at=self.parse_datetime(date_text),
                    excerpt=summary,
                    collection_method="html_list",
                )
            )
            if len(items) >= config.max_items_per_run:
                break
        return items
