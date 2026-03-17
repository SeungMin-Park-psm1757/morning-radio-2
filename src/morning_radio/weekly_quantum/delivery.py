from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

import requests

from .config import WeeklyQuantumConfig
from .models import DeliveryResult

TELEGRAM_MAX_MESSAGE = 3500


def deliver_weekly_bundle(
    *,
    config: WeeklyQuantumConfig,
    digest_markdown: str,
    title: str,
    full_audio_path: Path | None,
    public_links: dict[str, str] | None = None,
) -> DeliveryResult:
    result = DeliveryResult()
    if not config.telegram_enabled:
        result.errors.append("telegram_disabled")
        return result

    digest_html = _append_public_links(_markdown_to_telegram_html(digest_markdown), public_links)
    try:
        message_ids = _send_text_chunks(config, digest_html)
        result.text_sent = True
        result.message_ids.extend(message_ids)
    except Exception as exc:
        result.errors.append(f"telegram_text_failed:{exc}")

    if full_audio_path is not None and not full_audio_path.exists():
        result.errors.append("weekly_full_missing")
    elif full_audio_path is not None:
        try:
            message_id = _send_audio_bundle(config, full_audio_path, caption=f"{title} 전체본")
            result.full_audio_sent = True
            result.message_ids.append(message_id)
        except Exception as exc:
            result.errors.append(f"telegram_full_audio_failed:{exc}")

    return result


def public_links_for_run(
    *,
    config: WeeklyQuantumConfig,
    run_dir: Path,
    full_audio_path: Path | None,
) -> dict[str, str] | None:
    base_url = (config.public_archive_base_url or "").strip()
    if not base_url:
        return None

    base = base_url.rstrip("/")
    run_base = f"{base}/{run_dir.name}"
    links = {
        "summary": f"{run_base}/summary.md",
        "digest": f"{run_base}/message_digest.md",
    }
    if full_audio_path is not None and full_audio_path.exists():
        links["full_audio"] = f"{run_base}/{full_audio_path.name}"
    return links


def _send_text_chunks(config: WeeklyQuantumConfig, text: str) -> list[int]:
    message_ids: list[int] = []
    for chunk in _chunk_text(text, TELEGRAM_MAX_MESSAGE):
        payload: dict[str, Any] = {
            "chat_id": config.telegram_chat_id,
            "text": chunk,
            "disable_web_page_preview": True,
            "disable_notification": config.telegram_silent,
            "parse_mode": "HTML",
        }
        if config.telegram_thread_id:
            payload["message_thread_id"] = config.telegram_thread_id
        response = _telegram_post(config, "sendMessage", data=payload, timeout=30)
        message_ids.append(int(response["message_id"]))
    return message_ids


def _send_audio_bundle(config: WeeklyQuantumConfig, audio_path: Path, *, caption: str) -> int:
    payload: dict[str, Any] = {
        "chat_id": config.telegram_chat_id,
        "caption": caption,
        "title": audio_path.stem,
        "disable_notification": config.telegram_silent,
    }
    if config.telegram_thread_id:
        payload["message_thread_id"] = config.telegram_thread_id

    last_audio_error: Exception | None = None
    for attempt in range(config.retry_count + 1):
        try:
            with audio_path.open("rb") as handle:
                response = requests.post(
                    f"https://api.telegram.org/bot{config.telegram_bot_token}/sendAudio",
                    data=payload,
                    files={"audio": (audio_path.name, handle, "audio/mpeg")},
                    timeout=60,
                )
            response.raise_for_status()
            payload_json = response.json()
            if not payload_json.get("ok"):
                raise ValueError(f"Telegram sendAudio failed: {payload_json}")
            return int(payload_json["result"]["message_id"])
        except requests.HTTPError as exc:
            last_audio_error = exc
            break
        except Exception as exc:
            last_audio_error = exc
            if attempt >= config.retry_count:
                break

    document_payload: dict[str, Any] = {
        "chat_id": config.telegram_chat_id,
        "caption": caption,
        "disable_notification": config.telegram_silent,
    }
    if config.telegram_thread_id:
        document_payload["message_thread_id"] = config.telegram_thread_id

    last_document_error: Exception | None = None
    for attempt in range(config.retry_count + 1):
        try:
            with audio_path.open("rb") as handle:
                response = requests.post(
                    f"https://api.telegram.org/bot{config.telegram_bot_token}/sendDocument",
                    data=document_payload,
                    files={"document": (audio_path.name, handle)},
                    timeout=60,
                )
            response.raise_for_status()
            payload_json = response.json()
            if not payload_json.get("ok"):
                raise ValueError(f"Telegram sendDocument failed: {payload_json}")
            return int(payload_json["result"]["message_id"])
        except Exception as exc:
            last_document_error = exc
            if attempt >= config.retry_count:
                break

    raise RuntimeError(last_document_error or last_audio_error or "Telegram audio upload failed.")


def _telegram_post(
    config: WeeklyQuantumConfig,
    method: str,
    *,
    data: dict[str, Any],
    timeout: int,
    files: dict[str, Any] | None = None,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(config.retry_count + 1):
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{config.telegram_bot_token}/{method}",
                data=data,
                files=files,
                timeout=timeout,
            )
            response.raise_for_status()
            payload = response.json()
            if not payload.get("ok"):
                raise ValueError(f"Telegram {method} failed: {payload}")
            return payload["result"]
        except Exception as exc:
            last_error = exc
            if attempt >= config.retry_count:
                break
    raise RuntimeError(last_error or f"Telegram {method} failed")


def _append_public_links(text: str, public_links: dict[str, str] | None) -> str:
    if not public_links:
        return text

    labels = (
        ("summary", "실행 요약"),
        ("digest", "메시지 요약"),
        ("full_audio", "전체 MP3"),
    )
    lines = ["<b>바로가기</b>"]
    for key, label in labels:
        url = (public_links.get(key) or "").strip()
        if not url:
            continue
        lines.append(f"- <a href=\"{html.escape(url, quote=True)}\">{html.escape(label)}</a>")
    if len(lines) == 1:
        return text
    return f"{text}\n\n" + "\n".join(lines)


def _markdown_to_telegram_html(markdown: str) -> str:
    lines: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.startswith("# "):
            lines.append(f"<b>{html.escape(line[2:])}</b>")
            continue
        if line.startswith("## "):
            lines.append("")
            lines.append(f"<b>{html.escape(line[3:])}</b>")
            continue
        if line.startswith("- **") and line.endswith("**"):
            lines.append(f"- <b>{html.escape(line[4:-2])}</b>")
            continue
        if line.startswith("  "):
            lines.append(_inline_markdown_to_html(line.strip()))
            continue
        lines.append(html.escape(line))
    return "\n".join(lines).strip()


def _inline_markdown_to_html(text: str) -> str:
    escaped = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)


def _chunk_text(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    current = ""
    for paragraph in text.split("\n\n"):
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= limit:
            current = candidate
            continue
        if current:
            chunks.append(current)
            current = ""
        if len(paragraph) <= limit:
            current = paragraph
            continue

        lines = paragraph.splitlines()
        partial = ""
        for line in lines:
            candidate_line = line if not partial else f"{partial}\n{line}"
            if len(candidate_line) <= limit:
                partial = candidate_line
                continue
            if partial:
                chunks.append(partial)
            partial = line
        current = partial

    if current:
        chunks.append(current)
    return chunks
