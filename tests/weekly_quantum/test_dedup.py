from morning_radio.weekly_quantum.dedup import cluster_articles, exact_dedup, likely_duplicate
from morning_radio.weekly_quantum.models import NormalizedArticle, RawArticle


def make_item(title: str, source_key: str, url: str) -> NormalizedArticle:
    raw = RawArticle(
        source_key=source_key,
        source_label=source_key,
        source_url=url,
        section_key="test",
        title=title,
        canonical_url=url,
    )
    return NormalizedArticle(raw=raw, normalized_title=title, title_tokens=title.lower().split())


def test_exact_dedup_removes_same_title():
    a = make_item("IBM reveals new quantum roadmap", "tqi_daily", "https://a")
    b = make_item("IBM reveals new quantum roadmap", "qcr_news", "https://b")
    kept = exact_dedup([a, b])
    assert len(kept) == 1


def test_likely_duplicate_for_overlap():
    a = make_item("IBM reveals new quantum roadmap", "tqi_daily", "https://a")
    b = make_item("New quantum roadmap revealed by IBM", "qcr_news", "https://b")
    assert likely_duplicate(a, b)


def test_cluster_articles_groups_related_titles():
    a = make_item("IBM reveals new quantum roadmap", "tqi_daily", "https://a")
    b = make_item("New quantum roadmap revealed by IBM", "qcr_news", "https://b")
    c = make_item("Physicists improve quantum dots", "physorg_quantum", "https://c")
    clusters = cluster_articles([a, b, c])
    assert len(clusters) == 2
