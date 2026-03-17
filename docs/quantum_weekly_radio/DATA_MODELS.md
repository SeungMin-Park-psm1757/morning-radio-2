# Data Models

## 1. RawArticle

Represents the first-pass collected record from a feed or list page.

Fields:
- `source_key: str`
- `source_label: str`
- `source_url: str`
- `section_key: str`
- `title: str`
- `canonical_url: str`
- `published_at: datetime | None`
- `author: str | None`
- `excerpt: str`
- `site_brief_bullets: list[str]`
- `language_hint: str | None`
- `tags: list[str]`
- `raw_confidence: float`
- `collection_method: str`  # rss | html_list | html_detail | meta_only | title_only
- `detail_fetch_attempted: bool`
- `detail_fetch_succeeded: bool`

## 2. NormalizedArticle

A cleaned record suitable for scoring and clustering.

Additional fields:
- `normalized_title: str`
- `title_tokens: list[str]`
- `published_bucket: str`
- `is_hard_news: bool`
- `reliability_weight: float`
- `signal_terms: list[str]`
- `score: float`

## 3. StoryCluster

Fields:
- `cluster_id: str`
- `representative_url: str`
- `member_urls: list[str]`
- `cluster_size: int`
- `source_keys: list[str]`
- `dominant_section: str`
- `cluster_score: float`

## 4. BriefItem

Fields:
- `headline: str`
- `summary: str`
- `why_it_matters: str`
- `sources: list[str]`
- `cluster_id: str`
- `confidence: str`

## 5. CategoryBrief

Fields:
- `category_key: str`
- `category_label: str`
- `items: list[BriefItem]`
- `lead_summary: str`

## 6. WeeklyShow

Fields:
- `window_start: datetime`
- `window_end: datetime`
- `host_name: str`
- `analyst_name: str`
- `opening: str`
- `segments: list[dict]`
- `closing: str`
- `headline_script_text: str`
- `full_script_text: str`

## 7. SourceHealth

Fields:
- `source_key: str`
- `requested: bool`
- `success: bool`
- `http_status: int | None`
- `items_seen: int`
- `items_in_window: int`
- `detail_fetches: int`
- `fallback_mode_used: str | None`
- `error: str | None`
- `latency_ms: int | None`

## 8. WeeklyRunState

Fields:
- `last_attempt_started_at: datetime | None`
- `last_successful_window_end: datetime | None`
- `last_successful_run_dir: str | None`
- `last_delivery_status: str | None`
- `last_source_health: list[SourceHealth]`

## 9. Output files

Recommended run outputs:
- `raw_items.json`
- `normalized_items.json`
- `clusters.json`
- `selected_items.json`
- `category_briefs.json`
- `weekly_show.json`
- `weekly_script.md`
- `weekly_script.txt`
- `weekly_headlines.txt`
- `message_digest.md`
- `source_health.json`
- `summary.md`
- `run_metadata.json`
- `weekly_full.mp3`
