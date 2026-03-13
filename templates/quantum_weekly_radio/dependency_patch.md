# Dependency patch suggestion

The current repo already depends on:
- requests
- feedparser
- python-dateutil
- google-genai
- lameenc

Recommended additions for direct site collection:
- `beautifulsoup4>=4.12.3`
- `lxml>=5.3.0`

Suggested patch in `pyproject.toml`:

```toml
dependencies = [
  "feedparser>=6.0.11",
  "google-genai>=1.66.0",
  "lameenc>=1.8.1",
  "python-dateutil>=2.9.0",
  "requests>=2.32.0",
  "beautifulsoup4>=4.12.3",
  "lxml>=5.3.0",
]
```

If you want HTML parsing to stay optional, gate collectors so RSS-only sources still work without detail parsing.
