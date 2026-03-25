from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup, NavigableString, Tag

from ..models import RawArticle
from .base import BaseCollector, CollectorResult, SourceConfig

_BOARD_BASE_URL = "https://www.fqcf.org/niabbs5/"
_LIST_URL_TEMPLATE = "https://www.fqcf.org/niabbs5/bbs.php?bbstable=news&page={page}"
_LIST_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
_POSTED_AT_RE = re.compile(r"posted\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", flags=re.IGNORECASE)
_SOURCE_PREFIX_RE = re.compile(r"^\[(.+?)\]\s*(.+)$")
_SECTION_MARKERS = {"국내동향": "domestic", "해외동향": "international"}
_KST = ZoneInfo("Asia/Seoul")


@dataclass(slots=True)
class IssueEntry:
    detail_url: str
    title: str
    listed_at: datetime | None


class FQCFCollector(BaseCollector):
    def collect(self, config: SourceConfig) -> CollectorResult:
        started_at = time.perf_counter()
        items: list[RawArticle] = []
        detail_fetches = 0
        last_status: int | None = None
        errors: list[str] = []

        try:
            for page in range(1, 4):
                html, status_code = self.fetch_text(_LIST_URL_TEMPLATE.format(page=page))
                last_status = status_code
                entries = self._parse_list_page(html)
                if not entries:
                    break

                for entry in entries:
                    detail_fetches += 1
                    try:
                        detail_html, _ = self.fetch_text(entry.detail_url)
                        items.extend(self._parse_detail_page(detail_html, config, entry))
                    except Exception as exc:
                        errors.append(f"{entry.detail_url}: {exc}")
                    if len(items) >= config.max_items_per_run:
                        break

                if len(items) >= config.max_items_per_run:
                    break

            limited_items = items[: config.max_items_per_run]
            if limited_items:
                health = self.build_health(
                    source_key=config.key,
                    started_at=started_at,
                    success=True,
                    items_seen=len(limited_items),
                    http_status=last_status,
                    fallback_mode_used="html_issue_links",
                    error="; ".join(errors[:2]) if errors else None,
                )
                health.detail_fetches = detail_fetches
                return CollectorResult(items=limited_items, health=health)
        except Exception as exc:
            errors.append(str(exc))

        health = self.build_health(
            source_key=config.key,
            started_at=started_at,
            success=False,
            http_status=last_status,
            fallback_mode_used="html_issue_links_failed",
            error="; ".join(errors[:2]) if errors else "No FQCF issue links were collected.",
        )
        health.detail_fetches = detail_fetches
        return CollectorResult(items=[], health=health)

    def _parse_list_page(self, html: str) -> list[IssueEntry]:
        soup = BeautifulSoup(html, "html.parser")
        entries: list[IssueEntry] = []
        seen_urls: set[str] = set()

        for anchor in soup.select("a[href*='bbstable=news'][href*='call=read']"):
            title = anchor.get_text(" ", strip=True)
            if "[Daily Quantum]" not in title:
                continue

            detail_url = urljoin(_BOARD_BASE_URL, anchor.get("href", "").strip())
            if not detail_url or detail_url in seen_urls:
                continue

            row = anchor.find_parent("tr")
            row_text = row.get_text(" ", strip=True) if row else title
            listed_at = self._parse_listed_at(row_text)
            entries.append(IssueEntry(detail_url=detail_url, title=title, listed_at=listed_at))
            seen_urls.add(detail_url)

        return entries

    def _parse_detail_page(self, html: str, config: SourceConfig, entry: IssueEntry) -> list[RawArticle]:
        soup = BeautifulSoup(html, "html.parser")
        published_at = self._extract_posted_at(soup.get_text(" ", strip=True)) or entry.listed_at
        items: list[RawArticle] = []
        seen_urls: set[str] = set()

        for anchor in soup.select("a[href]"):
            href = urljoin(entry.detail_url, anchor.get("href", "").strip())
            if not href.startswith(("http://", "https://")):
                continue
            if "fqcf.org" in urlparse(href).netloc.casefold():
                continue
            if href in seen_urls:
                continue

            raw_title = anchor.get_text(" ", strip=True)
            if not raw_title:
                continue

            source_label, title = self._split_source_label(raw_title, href)
            excerpt, attempted, succeeded = self._fetch_external_excerpt(href)
            section_key = self._detect_section(anchor)
            tags = ["fqcf_daily", source_label]
            if section_key != "general":
                tags.append(section_key)

            items.append(
                RawArticle(
                    source_key=config.key,
                    source_label=source_label,
                    source_url=entry.detail_url,
                    section_key=section_key,
                    title=title,
                    canonical_url=href,
                    published_at=published_at,
                    excerpt=excerpt,
                    tags=tags,
                    raw_confidence=0.8 if succeeded else 0.65,
                    collection_method="html_issue_links",
                    detail_fetch_attempted=attempted,
                    detail_fetch_succeeded=succeeded,
                )
            )
            seen_urls.add(href)

        return items

    def _parse_listed_at(self, text: str) -> datetime | None:
        match = _LIST_DATE_RE.search(text)
        if not match:
            return None
        parsed = datetime.fromisoformat(match.group(1))
        return parsed.replace(tzinfo=_KST).astimezone(UTC)

    def _extract_posted_at(self, text: str) -> datetime | None:
        match = _POSTED_AT_RE.search(text)
        if not match:
            return None
        parsed = datetime.fromisoformat(match.group(1))
        return parsed.replace(tzinfo=_KST).astimezone(UTC)

    def _split_source_label(self, raw_title: str, url: str) -> tuple[str, str]:
        match = _SOURCE_PREFIX_RE.match(raw_title)
        if match:
            return match.group(1).strip(), match.group(2).strip()

        domain = urlparse(url).netloc.lower().strip()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain or "FQCF Daily Quantum", raw_title.strip()

    def _detect_section(self, anchor: Tag) -> str:
        for index, node in enumerate(anchor.previous_elements):
            if index >= 200:
                break
            if isinstance(node, NavigableString):
                text = " ".join(str(node).split())
                if text in _SECTION_MARKERS:
                    return _SECTION_MARKERS[text]
        return "general"

    def _fetch_external_excerpt(self, url: str) -> tuple[str, bool, bool]:
        try:
            html, _ = self.fetch_text(url)
        except Exception:
            return "", True, False

        soup = BeautifulSoup(html[:250000], "html.parser")
        for attrs in (
            {"property": "og:description"},
            {"name": "description"},
            {"name": "twitter:description"},
        ):
            meta = soup.find("meta", attrs=attrs)
            content = meta.get("content", "").strip() if meta else ""
            if content:
                return self.html_to_text(content)[:500], True, True
        return "", True, False
