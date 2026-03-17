---
name: migrate_google_news_to_direct_source_collectors
description: Replace or supplement Google-News-query collection with direct site collectors for the approved weekly quantum sources.
---


    # Migrate Google News to Direct Source Collectors

    Use this skill when the current news collection must shift from query-based Google News feeds to direct source adapters.

    ## Scope
    - Build source-specific collectors
    - Keep the current daily query collector intact unless explicitly asked to remove it
    - Use direct collection only for the weekly quantum system

    ## Read first
    - `docs/quantum_weekly_radio/SOURCE_MATRIX.md`
    - `docs/quantum_weekly_radio/FALLBACK_POLICY.md`
    - `templates/quantum_weekly_radio/config/sites.yaml`

    ## Rules
    - Start with list pages and RSS
    - Avoid full-body crawling for every article
    - Add timeouts, retries, and per-source caps
    - Record source health
    - Use title/excerpt/date/url extraction first

    ## Fallback ladder
    1. RSS
    2. HTML list page
    3. detail-page meta description
    4. title-only mode

    ## Deliverables
    - collector base contract
    - per-source collector modules
    - source health output
    - tests for config and parsing assumptions

