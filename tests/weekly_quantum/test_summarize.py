from datetime import UTC, datetime

from morning_radio.weekly_quantum.models import RawArticle, StoryCluster
from morning_radio.weekly_quantum.normalize import normalize_article
from morning_radio.weekly_quantum.summarize import categorize_cluster, heuristic_briefs


def _cluster(source_key: str, section_key: str, title: str) -> StoryCluster:
    raw = RawArticle(
        source_key=source_key,
        source_label=source_key,
        source_url=f"https://example.com/{source_key}/",
        section_key=section_key,
        title=title,
        canonical_url=f"https://example.com/{source_key}/{title.replace(' ', '-').lower()}",
        published_at=datetime(2026, 3, 16, 0, 0, tzinfo=UTC),
        excerpt=f"{title} excerpt",
    )
    normalized = normalize_article(raw)
    return StoryCluster(
        cluster_id=f"{source_key}-01",
        representative=normalized,
        members=[normalized],
        cluster_score=10.0,
    )


def test_categorize_cluster_uses_source_and_section_signals():
    assert categorize_cluster(_cluster("tqi_business", "business", "Quantum startup lands new funding")).key == "industry_business"
    assert categorize_cluster(_cluster("physorg_quantum", "research", "Qubit experiment improves coherence")).key == "research_technology"
    assert categorize_cluster(_cluster("tqi_national", "national", "Government expands quantum policy roadmap")).key == "policy_ecosystem"
    assert categorize_cluster(_cluster("qcr_qnalysis", "qnalysis", "Why the market is rethinking fault tolerance")).key == "analysis_outlook"


def test_heuristic_briefs_group_clusters_by_category():
    briefs = heuristic_briefs(
        [
            _cluster("tqi_business", "business", "Quantum startup lands new funding"),
            _cluster("physorg_quantum", "research", "Qubit experiment improves coherence"),
            _cluster("qcr_qnalysis", "qnalysis", "Why the market is rethinking fault tolerance"),
        ]
    )

    assert [brief.category_key for brief in briefs] == [
        "industry_business",
        "research_technology",
        "analysis_outlook",
    ]
    assert briefs[0].items[0].headline == "Quantum startup lands new funding"
    assert briefs[0].items[0].easy_explainer
    assert briefs[1].lead_summary
