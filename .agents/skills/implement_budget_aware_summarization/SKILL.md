---
name: implement_budget_aware_summarization
description: Build a low-token weekly summarization pipeline that favors list-page excerpts, RSS summaries, and site-provided bullets over full article bodies.
---


    # Implement Budget-Aware Summarization

    Use this skill when building or refining the weekly summary generation path.

    ## Read first
    - `docs/quantum_weekly_radio/API_BUDGET_STRATEGY.md`
    - `docs/quantum_weekly_radio/FALLBACK_POLICY.md`

    ## Rules
    - never summarize every collected article with the model
    - summarize representatives only
    - prefer cheap summaries:
      - RSS summary
      - list excerpt
      - site-provided bullet brief
      - meta description
    - expand detail pages only for top-ranked representatives

    ## Required outputs
    - category briefs
    - concise “what happened”
    - concise “why it matters”
    - confidence labels or degraded-mode markers

    ## Fallback
    If the model fails or quota is tight:
    - produce deterministic briefs from title + excerpt
    - keep output structured and honest

