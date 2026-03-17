from __future__ import annotations

from datetime import UTC, datetime

from .models import NormalizedArticle, StoryCluster

SOURCE_WEIGHTS = {
    "tqi_daily": 1.2,
    "tqi_national": 1.15,
    "tqi_business": 1.15,
    "tqi_research": 1.1,
    "tqi_education": 0.95,
    "tqi_insights": 0.95,
    "physorg_quantum": 1.1,
    "quantumzeitgeist_research": 1.0,
    "qcr_news": 1.1,
    "qcr_our_take": 0.95,
    "qcr_qnalysis": 1.0,
    "quantumfrontiers_news": 0.9,
}


def score_article(item: NormalizedArticle, *, now: datetime) -> float:
    score = 0.0
    if item.raw.published_at:
        hours = max(
            1.0,
            (now.astimezone(UTC) - item.raw.published_at.astimezone(UTC)).total_seconds() / 3600.0,
        )
        score += max(0.0, 168.0 - min(hours, 168.0)) / 24.0

    item.reliability_weight = SOURCE_WEIGHTS.get(item.raw.source_key, 1.0)
    score += item.reliability_weight
    score += min(len(item.raw.site_brief_bullets), 3) * 0.4
    if item.raw.excerpt:
        score += 0.5
    if item.is_hard_news:
        score += 0.25

    item.score = score
    return score


def score_cluster(cluster: StoryCluster) -> float:
    representative_score = cluster.representative.score
    multi_source_bonus = len({member.raw.source_key for member in cluster.members}) * 0.2
    size_bonus = min(len(cluster.members), 4) * 0.1
    hard_news_bonus = 0.25 if cluster.representative.is_hard_news else 0.0
    cluster.cluster_score = representative_score + multi_source_bonus + size_bonus + hard_news_bonus
    return cluster.cluster_score


def select_top_clusters(clusters: list[StoryCluster], limit: int) -> list[StoryCluster]:
    ordered = sorted(clusters, key=lambda cluster: cluster.cluster_score, reverse=True)
    return ordered[:limit]
