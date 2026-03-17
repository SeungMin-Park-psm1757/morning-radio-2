---
name: implement_tts_and_telegram_delivery_bundle
description: Implement the final delivery bundle for the weekly quantum system: Telegram text digest plus full and headlines MP3 files, with graceful partial-failure handling.
---


    # Implement TTS and Telegram Delivery Bundle

    Use this skill when the task is to deliver the weekly package.

    ## Bundle requirements
    - weekly digest text
    - full MP3
    - headlines MP3

    ## Reuse when possible
    - existing Gemini TTS helper
    - existing Telegram send logic
    - existing chunking / retry conventions

    ## Required behaviors
    - partial failure should not erase successful artifacts
    - still deliver text when TTS fails
    - still store run metadata when Telegram fails
    - support quiet / thread-aware Telegram delivery

    ## Suggested order
    1. write script text files
    2. generate audio files
    3. send digest text
    4. send audio files
    5. record delivery results

