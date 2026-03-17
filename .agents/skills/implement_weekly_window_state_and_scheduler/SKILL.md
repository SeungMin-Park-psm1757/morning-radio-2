---
name: implement_weekly_window_state_and_scheduler
description: Implement weekly run-state persistence, last-successful-run windowing, safe catch-up behavior, and a Monday 06:30 KST workflow.
---


    # Implement Weekly Window, State, and Scheduler

    Use this skill when working on state persistence, collection windows, or the scheduled workflow.

    ## Read first
    - `docs/quantum_weekly_radio/SCHEDULE_DELIVERY_PLAN.md`
    - `docs/quantum_weekly_radio/DATA_MODELS.md`
    - `templates/quantum_weekly_radio/workflows/weekly-quantum-radio.yml`

    ## Requirements
    - persist last successful run end time
    - support first-run bootstrap lookback
    - support safe catch-up after missed runs
    - allow manual override window
    - separate weekly output directory from daily output

    ## Workflow
    - keep `workflow_dispatch`
    - schedule for Monday 06:30 KST equivalent
    - upload artifacts
    - publish summary
    - optionally support heartbeat ping

    ## Anti-patterns
    - do not use naive “last 7 days” if state already exists
    - do not silently discard late windows

