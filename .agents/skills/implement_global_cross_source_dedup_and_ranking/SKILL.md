---
name: implement_global_cross_source_dedup_and_ranking
description: Implement exact dedup, canonical URL dedup, global cross-source near-duplicate clustering, representative selection, and weekly ranking rules.
---


    # Implement Global Cross-Source Dedup and Ranking

    Use this skill when the task centers on clustering, dedup, representative selection, or ranking.

    ## Goal
    Reuse the spirit of the existing repo’s duplicate-handling logic, but apply it across the full merged weekly source pool before expensive summarization.

    ## Required stages
    1. exact-title dedup
    2. canonical-URL dedup
    3. near-duplicate clustering
    4. representative selection
    5. weekly category quotas

    ## Heuristics to preserve
    - token overlap
    - Jaccard-like title similarity
    - signal token overlap
    - source diversity awareness

    ## Tests
    Write deterministic tests for:
    - same event across 2–3 sources
    - minor title wording changes
    - research stories with overlapping domain terms
    - non-duplicate stories that share only generic words

