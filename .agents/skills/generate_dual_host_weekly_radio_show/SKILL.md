---
name: generate_dual_host_weekly_radio_show
description: Generate a Korean dual-host weekly radio script plus a headlines-only version, using selected quantum stories and the repository’s existing radio-show style.
---


    # Generate Dual-Host Weekly Radio Show

    Use this skill when writing the final weekly script.

    ## Desired tone
    - Host: calm, reliable, organized
    - Analyst: brighter, contextual, never noisy

    ## Inputs
    - already selected stories
    - category briefs
    - weekly window metadata
    - optional watch-next-week notes

    ## Outputs
    - `weekly_script.md`
    - `weekly_script.txt`
    - `weekly_headlines.txt`

    ## Script goals
    - clearly summarize the week
    - avoid duplicate narration
    - connect industry, policy, research, and analysis sensibly
    - remain natural for TTS

    ## Do not
    - overstuff the script
    - repeat full source attribution every turn
    - exaggerate weak stories

