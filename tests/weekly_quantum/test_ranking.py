from datetime import UTC, datetime, timedelta

from morning_radio.weekly_quantum.models import RawArticle, StoryCluster
from morning_radio.weekly_quantum.normalize import normalize_article
from morning_radio.weekly_quantum.ranking import score_article, score_cluster, select_top_clusters


def _article(title: str, source_key: str, published_at: datetime):
    return normalize_article(
        RawArticle(
            source_key=source_key,
            source_label=source_key,
            source_url="https://example.com",
            section_key="news",
            title=title,
            canonical_url=f"https://example.com/{title.replace(' ', '-')}",
            published_at=published_at,
            excerpt="Short excerpt.",
        )
    )


def test_newer_article_scores_higher():
    now = datetime(2026, 3, 16, 0, 0, tzinfo=UTC)
    fresh = _article("Fresh quantum launch", "qcr_news", now - timedelta(hours=6))
    stale = _article("Older quantum launch", "qcr_news", now - timedelta(days=5))
    assert score_article(fresh, now=now) > score_article(stale, now=now)


def test_multi_source_cluster_gets_bonus():
    now = datetime(2026, 3, 16, 0, 0, tzinfo=UTC)
    left = _article("IBM quantum roadmap", "tqi_daily", now - timedelta(hours=3))
    right = _article("IBM quantum roadmap update", "qcr_news", now - timedelta(hours=2))
    solo = _article("Quantum dots progress", "physorg_quantum", now - timedelta(hours=2))
    score_article(left, now=now)
    score_article(right, now=now)
    score_article(solo, now=now)

    multi = StoryCluster(cluster_id="c1", representative=left, members=[left, right], cluster_score=0.0)
    single = StoryCluster(cluster_id="c2", representative=solo, members=[solo], cluster_score=0.0)
    assert score_cluster(multi) > score_cluster(single)
    assert select_top_clusters([single, multi], 1)[0].cluster_id == "c1"
