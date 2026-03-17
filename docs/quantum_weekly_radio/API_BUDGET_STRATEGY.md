# API Budget Strategy

## Goal

Keep Gemini / LLM usage low enough that high-volume weeks do not blow through quota.

## Core rule

Do not send every collected article to the model.

## 1. Budget tiers

### Low budget mode
- collect up to 60–80 items per source
- deduplicate globally
- select at most 10 representative stories for LLM
- generate only:
  - category briefs
  - final show script
- TTS only for 2 final scripts

### Standard mode
- detail-enrich 12–16 representatives
- add more context stories if quota permits

### Safe mode
- if API or quota risk is detected:
  - skip detail enrichment for lower-ranked clusters
  - generate heuristic category briefs
  - keep only one final LLM call for script if possible

## 2. Cheap signals first

Always prefer these sources of meaning before article body text:
- RSS summary
- list-page excerpt
- site-provided bullet brief
- meta description
- first 1–2 paragraphs only

## 3. Representative-only detail expansion

Flow:
1. collect all items
2. normalize
3. exact dedup
4. global cluster dedup
5. rank clusters
6. fetch detail only for top representatives

## 4. Hard caps

Suggested caps:
- max list items per source: 80
- max global candidates after window filter: 250
- max representatives after dedup: 20
- max detail fetches: 16
- max LLM stories used in final script prompt: 12

## 5. Prompt compression

Use structured input for the model.

Preferred object per story:
- headline
- source
- date
- short summary
- why it matters seed
- confidence

Avoid:
- raw HTML
- long article bodies
- repeated source metadata
- duplicate coverage text

## 6. TTS policy

Never TTS individual articles.
Only TTS:
- `weekly_script.txt`
- `weekly_headlines.txt`

## 7. Degraded mode

When budget is tight:
- keep deterministic ranking
- shorten final broadcast
- reduce story count
- skip optional context segments
- still deliver text digest even if TTS is disabled
