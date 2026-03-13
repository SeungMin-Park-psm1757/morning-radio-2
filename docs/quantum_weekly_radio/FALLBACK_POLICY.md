# Fallback Policy

## Philosophy

The weekly run should degrade gracefully instead of failing hard.

## 1. Collector fallback ladder

For each source:

1. RSS feed
2. category/list page HTML
3. detail-page meta description
4. title-only item
5. source skipped with health report

## 2. Missing timestamp

If a timestamp cannot be parsed:
- keep the item,
- mark confidence lower,
- exclude it from the top-ranked set unless the signal is unusually strong.

## 3. Detail fetch failure

If detail fetch fails:
- keep the list-page item,
- use excerpt/title-only summary,
- mark the item as lower confidence.

## 4. LLM failure

If LLM summarization fails:
- generate deterministic category briefs:
  - title
  - short excerpt
  - source label
- build a template-based script using the selected stories.
Do not abort the entire run.

## 5. TTS failure

If full TTS fails:
- still deliver text digest
- try headlines-only TTS
- record degraded mode

If headlines TTS fails:
- still deliver full text and full MP3 if available

## 6. Telegram failure

If text send fails:
- keep local run artifacts
- retry once or twice
- record failure in summary and source health

If audio upload fails:
- keep text delivery success
- record which file failed

## 7. Schedule failure or drift

If the scheduled workflow is late or missed:
- use last successful end time
- catch up on the next successful run
- do not silently shrink the time window to “last 7 days” if that would drop missed items

## 8. Source health output

Every run should produce a machine-readable source health file.
This is required for debugging and future alerting.
