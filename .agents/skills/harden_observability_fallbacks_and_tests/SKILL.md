---
name: harden_observability_fallbacks_and_tests
description: Add source-health reporting, degraded-mode summaries, smoke-test paths, workflow run summaries, and deterministic tests for the weekly quantum radio pipeline.
---


    # Harden Observability, Fallbacks, and Tests

    Use this skill when reliability work is the priority.

    ## Required outputs
    - `source_health.json`
    - `summary.md`
    - deterministic unit tests
    - smoke-run path for `--skip-llm --skip-tts`

    ## Include
    - source success/failure counts
    - fallback mode used per source
    - selected story counts
    - degraded mode markers
    - delivery status summary

    ## Test focus
    - time-window logic
    - dedup logic
    - ranking rules
    - source config validation
    - fallback behavior when detail fetching fails

