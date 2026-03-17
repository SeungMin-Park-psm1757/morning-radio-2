# Output Spec

## Directory
Recommended:
- `output/weekly_quantum/YYYYMMDD-HHMMSS/`

## Required files

### `raw_items.json`
All list-page or feed-collected items before normalization.

### `normalized_items.json`
Items after canonicalization and timestamp cleanup.

### `clusters.json`
Global clusters across every source.

### `selected_items.json`
The representatives chosen for weekly briefing.

### `category_briefs.json`
Structured brief objects per category.

### `weekly_show.json`
Machine-readable metadata for the generated show.

### `weekly_script.md`
Markdown dialogue script.

### `weekly_script.txt`
Plain text script for the full TTS pass.

### `weekly_headlines.txt`
Shorter headline-only TTS script.

### `message_digest.md`
Telegram-ready formatted digest.

### `source_health.json`
Per-source health and fallback details.

### `summary.md`
Run summary including:
- window
- source counts
- selected story counts
- degraded modes used
- delivery status

### `run_metadata.json`
A compact machine-readable object containing:
- version
- runtime
- config snapshot
- window
- output locations
- major flags

### Audio
- `weekly_full.mp3`

## Telegram format

### Message 1
Digest text:
- short intro
- 6–12 bullet-like story blocks
- one-line why-it-matters
- optional archive link

### Message 2
Full MP3 audio
