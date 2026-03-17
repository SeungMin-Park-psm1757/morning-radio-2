from __future__ import annotations

from dataclasses import asdict, dataclass, field
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
    language_hint: str | None = None
    tags: list[str] = field(default_factory=list)
    raw_confidence: float = 0.5
    collection_method: str = "html_list"
    detail_fetch_attempted: bool = False
    detail_fetch_succeeded: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.published_at is not None:
            payload["published_at"] = self.published_at.isoformat()
        return payload


@dataclass(slots=True)
class NormalizedArticle:
    raw: RawArticle
    normalized_title: str
    title_tokens: list[str]
    published_bucket: str = "unknown"
    is_hard_news: bool = False
    reliability_weight: float = 1.0
    signal_terms: list[str] = field(default_factory=list)
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw": self.raw.to_dict(),
            "normalized_title": self.normalized_title,
            "title_tokens": list(self.title_tokens),
            "published_bucket": self.published_bucket,
            "is_hard_news": self.is_hard_news,
            "reliability_weight": self.reliability_weight,
            "signal_terms": list(self.signal_terms),
            "score": self.score,
        }


@dataclass(slots=True)
class StoryCluster:
    cluster_id: str
    representative: NormalizedArticle
    members: list[NormalizedArticle]
    cluster_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "representative_url": self.representative.raw.canonical_url,
            "member_urls": [member.raw.canonical_url for member in self.members],
            "cluster_size": len(self.members),
            "source_keys": sorted({member.raw.source_key for member in self.members}),
            "dominant_section": self.representative.raw.section_key,
            "cluster_score": self.cluster_score,
            "representative": self.representative.to_dict(),
        }


@dataclass(slots=True)
class BriefItem:
    headline: str
    summary: str
    why_it_matters: str
    sources: list[str]
    cluster_id: str
    confidence: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CategoryBrief:
    category_key: str
    category_label: str
    items: list[BriefItem]
    lead_summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "category_key": self.category_key,
            "category_label": self.category_label,
            "items": [item.to_dict() for item in self.items],
            "lead_summary": self.lead_summary,
        }


@dataclass(slots=True)
class WeeklyShow:
    window_start: datetime
    window_end: datetime
    host_name: str
    analyst_name: str
    show_title: str
    show_summary: str
    opening: str
    segments: list[dict[str, Any]]
    closing: str
    headline_script_text: str
    full_script_text: str
    full_script_markdown: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "window_start": self.window_start.isoformat(),
            "window_end": self.window_end.isoformat(),
            "host_name": self.host_name,
            "analyst_name": self.analyst_name,
            "show_title": self.show_title,
            "show_summary": self.show_summary,
            "opening": self.opening,
            "segments": self.segments,
            "closing": self.closing,
            "headline_script_text": self.headline_script_text,
            "full_script_text": self.full_script_text,
            "full_script_markdown": self.full_script_markdown,
        }


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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
