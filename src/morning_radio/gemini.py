from __future__ import annotations

import json
import re
from typing import Any


def _extract_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if text:
        return text

    candidates = getattr(response, "candidates", None) or []
    parts: list[str] = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            value = getattr(part, "text", None)
            if value:
                parts.append(value)
    return "\n".join(parts).strip()


def _extract_json_payload(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```json\s*", "", cleaned)
        cleaned = re.sub(r"^```\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Model did not return a JSON object.")
    return json.loads(cleaned[start : end + 1])


def _markdown_to_plaintext(markdown: str) -> str:
    text = markdown.strip()
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    return text.strip()


def _format_tts_transcript(script_text: str, pause_multiplier: float) -> str:
    lines = [line.strip() for line in script_text.splitlines() if line.strip()]
    if pause_multiplier >= 1.7:
        separator = "\n\n\n\n"
    elif pause_multiplier >= 1.4:
        separator = "\n\n\n"
    else:
        separator = "\n\n"
    return separator.join(lines)


def _retry_delay_seconds(message: str, default_seconds: int) -> int:
    match = re.search(r"retry in ([0-9.]+)s", message, flags=re.IGNORECASE)
    if match:
        return max(1, int(float(match.group(1))) + 1)

    match = re.search(r"retryDelay['\"]?:\s*['\"]?(\d+)s", message, flags=re.IGNORECASE)
    if match:
        return max(1, int(match.group(1)))

    return max(1, default_seconds)
