# Morning Radio

This repository now ships only the weekly quantum briefing pipeline.

## What It Does

- Collects quantum news directly from approved sources and weekly digest pages.
- Includes FQCF Daily Quantum issue posts and expands each issue into its linked external articles.
- Deduplicates overlapping coverage across sources.
- Builds Korean category briefs, a two-speaker radio script, an optional full-length MP3, and a Telegram digest.
- Writes per-run artifacts under `output/weekly_quantum/YYYYMMDD-HHMMSS/`.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

Set `GEMINI_API_KEY` in your environment or `.env`, then run:

```bash
morning-radio
```

For a no-API smoke test:

```bash
morning-radio --skip-llm --skip-tts --dry-run
```

## Main Outputs

Each run writes to `output/weekly_quantum/YYYYMMDD-HHMMSS/`.

- `raw_items.json`
- `normalized_items.json`
- `clusters.json`
- `selected_items.json`
- `category_briefs.json`
- `weekly_show.json`
- `weekly_script.md`
- `weekly_script.txt`
- `weekly_headlines.txt`
- `message_digest.md`
- `summary.md`
- `source_health.json`
- `run_metadata.json`
- `weekly_full.mp3` when TTS succeeds

## GitHub Actions

The workflow is defined in `.github/workflows/weekly-quantum-radio.yml`.

- Schedule: Monday `06:00 KST`
- Entry point: `morning-radio` or `python -m morning_radio`
- Telegram delivery is enabled only when the Telegram secrets are present

## Notes

- The root CLI now points to the weekly quantum pipeline.
- Legacy daily news briefing code has been removed.
- Gemini generation and TTS both degrade safely when disabled or unavailable.
