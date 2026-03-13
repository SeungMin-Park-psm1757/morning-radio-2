# Research Notes

This project pack was designed around the current repository shape and the current source-site behavior.

## Existing repo observations
- Current repo root: `SeungMin-Park-psm1757/daily-news-summary`
- Current package path: `src/morning_radio/`
- Existing workflow path: `.github/workflows/daily-radio.yml`
- Current daily flow already produces digest/script/audio/archive/Telegram outputs.
- Current collection logic is Google-News-query based, not direct site-collector based.
- Current global exact-title dedup exists before grouping by category.
- Current near-duplicate clustering is article-level and should be reused/adapted for global cross-source dedup.

## Source-site observations used in this pack
- TQI category pages list post titles and dates clearly.
- TQI article pages can expose short “Insider Brief” bullets that are cheaper than full-body parsing.
- Phys.org has category pages and supports RSS feed usage.
- Quantum Zeitgeist category pages expose titles and dates.
- QCR exposes list-style news and analysis pages that are useful for list-first extraction.
- Quantum Frontiers offers RSS / posts feed and category pages.

## Schedule/ops observations used in this pack
- GitHub Actions schedule is UTC-based.
- Scheduled runs can be delayed or dropped under load, especially around the start of the hour.
- Public repositories can have scheduled workflows auto-disabled after inactivity.
