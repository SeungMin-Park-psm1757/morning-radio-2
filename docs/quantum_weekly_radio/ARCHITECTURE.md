# Architecture

## 1. Design principle

Build the weekly quantum system as an additive sub-pipeline inside the current repository.
Do not start by refactoring the current daily pipeline.
Stabilize the weekly path first, then optionally extract shared helpers later.

## 2. High-level flow

1. Load config and run-state
2. Determine collection window
3. Collect lightweight list items from each source
4. Normalize metadata
5. Run exact dedup + global near-duplicate clustering
6. Rank clusters and choose representatives
7. Expand details only for representatives
8. Build category briefs
9. Generate:
   - Telegram digest
   - full radio script
   - headlines-only script
10. Generate TTS:
   - weekly_full.mp3
11. Deliver to Telegram
12. Persist outputs + run state + source health

## 3. Component map

### Collectors
Each source gets its own adapter.

Responsibilities:
- fetch list pages or feeds
- parse title / url / published_at / excerpt
- optionally fetch lightweight article detail fields
- report source health and parse counts

### Normalizer
Responsibilities:
- canonical URL normalization
- timestamp parsing
- category mapping
- source labeling
- excerpt cleaning
- confidence flagging

### Global dedup
Responsibilities:
- exact-title dedup
- canonical-URL dedup
- near-duplicate clustering across all sources
- representative selection

### Ranking
Responsibilities:
- prioritize recency
- prioritize clearer source summaries
- prioritize source reliability / signal terms
- keep education/insight pieces from overwhelming hard-news items
- downweight low-signal or duplicate-heavy items

### Summarization
Responsibilities:
- budget-aware category briefs
- representative-only detail expansion
- short “what happened / why it matters” objects
- degraded heuristic mode when LLM is unavailable

### Script writer
Responsibilities:
- dual-host weekly show
- calm host + lighter analyst
- consistent weekly opening / closing
- produce:
  - full script
  - headlines-only script

### Delivery
Responsibilities:
- Telegram message chunking
- audio upload
- retry and partial-failure behavior

### State store
Responsibilities:
- persist last successful run
- persist source success/failure summary
- keep recovery simple and transparent

## 4. Output directory proposal

Recommended:
- `output/weekly_quantum/YYYYMMDD-HHMMSS/`

Keep the weekly outputs separate from the current daily output path.

## 5. Failure isolation

### Source-level failure
One source failing must not abort the whole run.

### LLM failure
Fallback to deterministic digest + template script.

### TTS failure
Still deliver text digest and mark degraded mode.

### Telegram failure
Keep local run artifacts and retry when possible.

### Schedule failure
Support manual rerun and state-safe catch-up.

## 6. Why additive namespace first

Benefits:
- lower risk to the working daily system
- easier testing
- easier rollback
- easier to compare design assumptions before merging shared logic
