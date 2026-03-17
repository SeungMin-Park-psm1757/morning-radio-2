from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class RawArticle:
    source_key: str
    source_label: str
    source_url: str
    section_key: str
    title: str
    canonical_url: str
    published_at: datetime | None = None
    author: str | None = None
    excerpt: str = ""
    site_brief_bullets: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    raw_confidence: float = 0.5
    collection_method: str = "html_list"
    detail_fetch_attempted: bool = False
    detail_fetch_succeeded: bool = False


@dataclass(slots=True)
class NormalizedArticle:
    raw: RawArticle
    normalized_title: str
    title_tokens: list[str]
    reliability_weight: float = 1.0
    signal_terms: list[str] = field(default_factory=list)
    is_hard_news: bool = False
    score: float = 0.0


@dataclass(slots=True)
class StoryCluster:
    cluster_id: str
    representative: NormalizedArticle
    members: list[NormalizedArticle]
    cluster_score: float


@dataclass(slots=True)
class BriefItem:
    headline: str
    summary: str
    why_it_matters: str
    sources: list[str]
    cluster_id: str
    confidence: str = "medium"


@dataclass(slots=True)
class CategoryBrief:
    category_key: str
    category_label: str
    items: list[BriefItem]
    lead_summary: str


@dataclass(slots=True)
class SourceHealth:
    source_key: str
    requested: bool = False
    success: bool = False
    http_status: int | None = None
    items_seen: int = 0
    items_in_window: int = 0
    detail_fetches: int = 0
    fallback_mode_used: str | None = None
    error: str | None = None
    latency_ms: int | None = None


@dataclass(slots=True)
class WeeklyRunState:
    last_attempt_started_at: datetime | None = None
    last_successful_window_end: datetime | None = None
    last_successful_run_dir: str | None = None
    last_delivery_status: str | None = None
    last_source_health: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class DeliveryResult:
    text_sent: bool = False
    full_audio_sent: bool = False
    headlines_audio_sent: bool = False
    message_ids: list[int] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
