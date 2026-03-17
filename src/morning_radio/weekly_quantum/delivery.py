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

    Keep failure reporting honest until the real Telegram integration lands.
    """
    result = DeliveryResult()
    if not enable_telegram:
        result.errors.append("telegram_disabled")
        return result

    missing: list[str] = []
    if not digest_path.exists():
        missing.append("digest")
    if full_audio_path is not None and not full_audio_path.exists():
        missing.append("weekly_full.mp3")
    if headlines_audio_path is not None and not headlines_audio_path.exists():
        missing.append("weekly_headlines.mp3")

    result.errors.append("telegram_delivery_not_implemented")
    if missing:
        result.errors.append("missing_artifacts:" + ",".join(missing))
    return result
