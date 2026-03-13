# MVP Task List

## Setup
- [ ] Add repo-level `AGENTS.md`
- [ ] Add `.agents/skills/`
- [ ] Add weekly docs and templates

## Code scaffold
- [ ] Create `src/morning_radio/weekly_quantum/`
- [ ] Add config loading
- [ ] Add run-state persistence
- [ ] Add output directory layout

## Collection
- [ ] Base collector interface
- [ ] TQI collector
- [ ] Phys.org collector
- [ ] Quantum Zeitgeist collector
- [ ] QCR collector
- [ ] Quantum Frontiers collector
- [ ] Source health reporting

## Processing
- [ ] Normalize timestamps and canonical URLs
- [ ] Exact dedup
- [ ] Global near-duplicate clustering
- [ ] Ranking
- [ ] Category quotas

## Generation
- [ ] Heuristic digest fallback
- [ ] LLM category briefs
- [ ] Full radio script
- [ ] Headlines-only script

## Delivery
- [ ] Full MP3 generation
- [ ] Headlines MP3 generation
- [ ] Telegram text send
- [ ] Telegram audio send
- [ ] Retry / partial-failure logic

## Operations
- [ ] Weekly workflow
- [ ] Manual dispatch path
- [ ] Artifact upload
- [ ] Summary output
- [ ] Heartbeat note

## Tests
- [ ] Dedup unit tests
- [ ] Run-state unit tests
- [ ] Source-config tests
- [ ] Smoke test for `--skip-llm --skip-tts`
