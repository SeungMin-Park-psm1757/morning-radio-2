from __future__ import annotations

from collections import defaultdict

from .models import NormalizedArticle, StoryCluster


def exact_dedup(items: list[NormalizedArticle]) -> list[NormalizedArticle]:
    seen_titles: set[str] = set()
    seen_urls: set[str] = set()
    kept: list[NormalizedArticle] = []

    for item in items:
        title_key = item.normalized_title.casefold()
        url_key = item.raw.canonical_url.casefold()
        if title_key in seen_titles or url_key in seen_urls:
            continue
        seen_titles.add(title_key)
        seen_urls.add(url_key)
        kept.append(item)
    return kept


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def likely_duplicate(left: NormalizedArticle, right: NormalizedArticle) -> bool:
    left_tokens = set(left.title_tokens)
    right_tokens = set(right.title_tokens)
    overlap = left_tokens & right_tokens

    if len(overlap) >= 3:
        return True

    if jaccard(left_tokens, right_tokens) >= 0.45:
        return True

    # Keep a light “signal token” concept like the current repo’s style:
    strong = {
        token for token in overlap
        if len(token) >= 5 or token.isdigit() or "-" in token
    }
    if len(strong) >= 2:
        return True

    return False


def cluster_articles(items: list[NormalizedArticle]) -> list[StoryCluster]:
    clusters: list[list[NormalizedArticle]] = []

    for article in items:
        placed = False
        for cluster in clusters:
            if any(likely_duplicate(article, member) for member in cluster):
                cluster.append(article)
                placed = True
                break
        if not placed:
            clusters.append([article])

    results: list[StoryCluster] = []
    for index, members in enumerate(clusters, start=1):
        representative = members[0]
        results.append(
            StoryCluster(
                cluster_id=f"global-{index:03d}",
                representative=representative,
                members=members,
                cluster_score=float(len(members)),
            )
        )
    return results


def cluster_sources(clusters: list[StoryCluster]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for cluster in clusters:
        for member in cluster.members:
            counts[member.raw.source_key] += 1
    return dict(counts)
