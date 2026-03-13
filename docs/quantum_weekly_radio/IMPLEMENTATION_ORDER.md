# Implementation Order

## Phase 1 — Safe scaffolding
- create `src/morning_radio/weekly_quantum/`
- create config, models, state store
- add new CLI entry path
- add dedicated weekly output path

## Phase 2 — Source collection
- implement collector base contract
- implement TQI collector
- implement Phys.org collector
- implement Quantum Zeitgeist collector
- implement QCR collectors
- implement Quantum Frontiers collector
- add source health reporting
- add per-source caps / retries / timeout

## Phase 3 — Global dedup and ranking
- port exact-title ideas
- implement canonical URL dedup
- implement cross-source clustering
- implement representative selection
- implement weekly ranking policy

## Phase 4 — Summary and script generation
- category briefs
- low-budget / heuristic fallback
- full weekly dialogue script
- headline-only script

## Phase 5 — Delivery
- full MP3
- headlines MP3
- Telegram text + audio bundle
- retry / degraded mode

## Phase 6 — Workflow and operations
- GitHub Actions workflow
- run-state persistence
- heartbeat / summary
- artifact upload

## Phase 7 — Tests
- time window tests
- dedup tests
- ranking tests
- source config tests
- fallback path tests

## Rule of thumb

Never start with fancy prompt tuning before:
- collection works,
- dedup works,
- outputs are stable,
- and state handling is safe.
