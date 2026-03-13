from __future__ import annotations

import re
from datetime import UTC
from urllib.parse import urlsplit, urlunsplit

from .models import NormalizedArticle, RawArticle

_TOKEN_RE = re.compile(r"[a-z0-9가-힣]+")
_HARD_NEWS_HINTS = ("daily", "national", "business", "research", "news")


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url)
    clean = parts._replace(query="", fragment="")
    return urlunsplit(clean).rstrip("/")


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title).strip()


def title_tokens(title: str) -> list[str]:
    return _TOKEN_RE.findall(title.lower())


def _published_bucket(raw: RawArticle) -> str:
    if raw.published_at is None:
        return "unknown"
    return raw.published_at.astimezone(UTC).strftime("%Y-%m-%d")


def normalize_article(raw: RawArticle) -> NormalizedArticle:
    normalized = RawArticle(
        source_key=raw.source_key,
        source_label=raw.source_label,
        source_url=raw.source_url,
        section_key=raw.section_key,
        title=normalize_title(raw.title),
        canonical_url=canonicalize_url(raw.canonical_url),
        published_at=raw.published_at,
        author=raw.author,
        excerpt=re.sub(r"\s+", " ", raw.excerpt).strip(),
        site_brief_bullets=list(raw.site_brief_bullets),
        language_hint=raw.language_hint,
        tags=list(raw.tags),
        raw_confidence=raw.raw_confidence,
        collection_method=raw.collection_method,
        detail_fetch_attempted=raw.detail_fetch_attempted,
        detail_fetch_succeeded=raw.detail_fetch_succeeded,
    )
    section_key = normalized.section_key.casefold()
    signal_terms = [token for token in title_tokens(normalized.title) if len(token) >= 6]
    return NormalizedArticle(
        raw=normalized,
        normalized_title=normalized.title,
        title_tokens=title_tokens(normalized.title),
        published_bucket=_published_bucket(normalized),
        is_hard_news=any(hint in section_key for hint in _HARD_NEWS_HINTS),
        signal_terms=signal_terms[:6],
    )
