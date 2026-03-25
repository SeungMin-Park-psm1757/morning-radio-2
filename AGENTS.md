# AGENTS.md

## Repository context

This repository now operates as a **weekly quantum-only** pipeline.
It:
- collects quantum article candidates directly from approved sources,
- ranks and clusters them,
- writes digest/script/output artifacts,
- optionally generates TTS audio,
- and delivers results to Telegram.

Some planning documents still describe the earlier migration plan from a daily pipeline. Treat those references as historical context, not a current requirement.

## Primary goal

Maintain the pipeline that:
- runs every Monday 06:00 KST,
- covers the last successful-run window for the approved quantum source sites,
- gathers articles directly from site category pages / RSS / lightweight detail pages,
- deduplicates globally across all sources,
- produces:
  - one Telegram-friendly weekly text digest,
  - one full-length MP3,
  - one headlines-only MP3,
- and remains usable when some sources or APIs partially fail.

## Working rules

1. Prefer **additive implementation** under:
   - `src/morning_radio/weekly_quantum/`
   - `.github/workflows/weekly-quantum-radio.yml`
   - `tests/weekly_quantum/`

2. The root CLI should continue to launch the weekly pipeline.

3. Reuse existing repo modules when safe:
   - Gemini text generation
   - Gemini TTS
   - Telegram sending
   - output/archive helpers
   - current duplicate-clustering ideas

4. Before touching summarization, implement:
   - source adapter contract,
   - weekly state window,
   - global dedup layer,
   - source health reporting.

5. Minimize API spend:
   - collect list-page metadata first,
   - deduplicate before expensive steps,
   - fetch detail pages only for representatives,
   - send only final scripts to TTS.

6. Prefer storing:
   - title
   - source
   - category
   - published_at
   - canonical_url
   - short excerpt
   - site-provided bullets if available
   - generated summary
   - cluster metadata
   Avoid storing full article bodies unless the user asks or a debug mode is enabled.

7. Every phase must preserve a smoke path:
   - `--skip-llm`
   - `--skip-tts`

8. All networked collectors must have:
   - timeout
   - retry policy
   - per-source caps
   - fallback mode
   - source health output

9. Use type hints.
10. Keep comments concise and operational.
11. Add tests for deterministic logic first:
   - time-window handling
   - dedup
   - ranking
   - fallback selection
   - source config validation

## Definition of done

A task is not done unless:
- implementation matches the docs in `docs/quantum_weekly_radio/`,
- the code path is additive and understandable,
- outputs are written under a dedicated weekly output path,
- there is at least one test or smoke-run validation for the new logic,
- failure modes are reported rather than silently swallowed.

## Documents to read first

Always read these before coding a new weekly-quantum task:
- `docs/quantum_weekly_radio/PROJECT_BRIEF_FOR_CODEX.md`
- `docs/quantum_weekly_radio/ARCHITECTURE.md`
- `docs/quantum_weekly_radio/IMPLEMENTATION_ORDER.md`
- `docs/quantum_weekly_radio/API_BUDGET_STRATEGY.md`
- `docs/quantum_weekly_radio/FALLBACK_POLICY.md`

## Skills

Relevant skills live under `.agents/skills/`.
Use the most specific skill that matches the current task.
