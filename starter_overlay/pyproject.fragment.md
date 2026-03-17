# pyproject fragment suggestion

Add a new console script if desired:

```toml
[project.scripts]
morning-radio-weekly-quantum = "morning_radio.weekly_quantum.cli:main"
```

And add HTML parsing dependencies if direct HTML collection is implemented:

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
