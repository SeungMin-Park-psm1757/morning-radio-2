---
name: build_quantum_weekly_radio_system
description: Build the full weekly quantum morning-radio pipeline inside the existing repository, using additive modules, direct source collectors, global dedup, budget-aware summarization, TTS, and Telegram delivery.
---


    # Build Quantum Weekly Radio System

    Use this skill when the task is to build or significantly revise the full weekly quantum radio feature.

    ## Read first
    - `AGENTS.md`
    - `docs/quantum_weekly_radio/PROJECT_BRIEF_FOR_CODEX.md`
    - `docs/quantum_weekly_radio/ARCHITECTURE.md`
    - `docs/quantum_weekly_radio/IMPLEMENTATION_ORDER.md`

    ## Goal
    Extend the current repository with a weekly quantum-only pipeline that:
    - runs Monday 06:30 KST,
    - collects directly from approved sites,
    - deduplicates globally,
    - produces one digest plus two MP3 files,
    - and delivers them to Telegram.

    ## Working style
    - Prefer additive implementation.
    - Create new weekly code under `src/morning_radio/weekly_quantum/`.
    - Keep the current daily system stable.
    - Reuse existing Gemini/TTS/Telegram helpers where safe.

    ## Recommended order
    1. scaffolding
    2. collectors
    3. normalization and window/state
    4. global dedup and ranking
    5. summary generation
    6. script generation
    7. TTS + Telegram delivery
    8. workflow + tests

    ## Done when
    - manual CLI works,
    - workflow file exists,
    - smoke mode exists,
    - outputs match `docs/quantum_weekly_radio/OUTPUT_SPEC.md`,
    - and deterministic tests exist for the core logic.

