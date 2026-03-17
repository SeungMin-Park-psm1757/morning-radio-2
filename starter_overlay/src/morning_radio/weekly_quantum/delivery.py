from __future__ import annotations

from pathlib import Path

from .models import DeliveryResult


def deliver_weekly_bundle(
    *,
    digest_path: Path,
    full_audio_path: Path | None,
    headlines_audio_path: Path | None,
    enable_telegram: bool,
) -> DeliveryResult:
    """Placeholder delivery entrypoint.

    Replace with real integration that reuses the repo's existing Telegram helper.
    """
    result = DeliveryResult()
    if not enable_telegram:
        return result

    if digest_path.exists():
        result.text_sent = True
    if full_audio_path and full_audio_path.exists():
        result.full_audio_sent = True
    if headlines_audio_path and headlines_audio_path.exists():
        result.headlines_audio_sent = True
    return result
