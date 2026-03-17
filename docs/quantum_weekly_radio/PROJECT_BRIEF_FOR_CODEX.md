# Weekly Quantum Morning Radio – Codex Build Brief

## Mission

Extend the existing `morning_radio` repository with a new additive pipeline that creates a **weekly quantum-technology morning show**.

The new pipeline must:
- run every Monday at 06:00 KST,
- collect from the approved source sites below,
- reuse the current repo’s proven ranking / dedup / Telegram / TTS ideas where safe,
- and produce one weekly text digest plus one MP3 file.

## Approved source sites


- https://thequantuminsider.com/category/daily/
- https://thequantuminsider.com/category/daily/national/
- https://thequantuminsider.com/category/daily/business/
- https://thequantuminsider.com/category/daily/researchandtech/
- https://thequantuminsider.com/category/exclusives/education/
- https://thequantuminsider.com/category/exclusives/insights/
- https://phys.org/physics-news/quantum-physics/?hl=ko-KR
- https://quantumzeitgeist.com/category/quantum-research-news/
- https://quantumcomputingreport.com/news/
- https://quantumcomputingreport.com/our-take/
- https://quantumcomputingreport.com/qnalysis/
- https://quantumfrontiers.com/category/news/


## Required outputs

### External outputs
- weekly Telegram text digest
- `weekly_full.mp3`

### Internal run outputs
- `raw_items.json`
- `normalized_items.json`
- `clusters.json`
- `selected_items.json`
- `category_briefs.json`
- `weekly_script.md`
- `weekly_script.txt`
- `message_digest.md`
- `weekly_headlines.txt`
- `source_health.json`
- `run_metadata.json`
- `summary.md`

## Constraints

- Do not break the existing daily morning-radio workflow.
- Prefer additive work under `src/morning_radio/weekly_quantum/`.
- Implement direct site collectors instead of Google News query collection.
- Preserve the spirit of the current dedup logic, but make it global across all sources before expensive summarization.
- Keep API costs low by using list-page summaries / RSS summaries / site-provided bullets whenever possible.
- Fetch article detail pages only for deduplicated representatives.
- TTS should be used only for the final full weekly script.
- The system must continue working in degraded mode when:
  - one or more sources fail,
  - TTS fails,
  - LLM generation fails,
  - Telegram delivery partially fails.

## Architecture preference

Use a new package:
- `src/morning_radio/weekly_quantum/`

Suggested modules:
- `config.py`
- `models.py`
- `state_store.py`
- `normalize.py`
- `dedup.py`
- `ranking.py`
- `summarize.py`
- `script_writer.py`
- `delivery.py`
- `pipeline.py`
- `cli.py`
- `collectors/base.py`
- `collectors/*.py`

## State policy

Use last successful run timestamps to define the next collection window.
If there is no prior successful state, collect with a safe initial lookback window.

## Definition of done

The weekly quantum system is ready when:
1. the new CLI can run manually,
2. the new workflow can run on schedule,
3. global dedup works across all configured sources,
4. a smoke path exists for `--skip-llm --skip-tts`,
5. text digest and one MP3 deliverable are generated,
6. Telegram delivery is bundled,
7. source health is recorded,
8. tests exist for deterministic logic.
