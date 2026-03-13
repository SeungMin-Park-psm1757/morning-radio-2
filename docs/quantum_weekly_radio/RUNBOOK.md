# Operations Runbook

## Manual dry run
Recommended first:
- run collection with `--skip-llm --skip-tts --skip-telegram`
- inspect `raw_items.json`, `clusters.json`, `source_health.json`

## Manual real run
After collection stabilizes:
- run full pipeline
- verify digest text
- verify both MP3 files
- verify Telegram send

## Common failure cases

### A. One source returns zero items
Check:
- site HTML structure
- date parsing
- time window too narrow
- robots / rate limiting
- fallback mode output

### B. Too many stories selected
Check:
- clustering thresholds
- category quotas
- list item cap
- signal score inflation

### C. Token budget spike
Check:
- detail fetch count
- stories sent to LLM
- unnecessary full-body collection
- long prompts with repeated metadata

### D. Telegram audio fails
Check:
- file path
- file size
- timeout
- bot permissions
- chat / thread ID

### E. Schedule missed
Check:
- Actions workflow status
- repo activity
- manual dispatch
- next run catch-up window

## Monthly maintenance
- review source selectors
- review per-source item caps
- review cluster thresholds
- review Telegram delivery reliability
- review inactivity risk if repo is quiet
