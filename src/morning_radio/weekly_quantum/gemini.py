from __future__ import annotations

import json
import time
from typing import Any

from google import genai
from google.genai import errors, types

from morning_radio.gemini import (
    _extract_json_payload,
    _extract_text,
    _format_tts_transcript,
    _markdown_to_plaintext,
    _retry_delay_seconds,
)

from .config import WeeklyQuantumConfig
from .models import BriefItem, CategoryBrief, StoryCluster, WeeklyShow
from .window import CollectionWindow


def _json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def _default_show_title(window: CollectionWindow) -> str:
    return f"주간 양자 브리핑 ({window.end.date().isoformat()})"


def _default_show_summary(briefs: list[CategoryBrief]) -> str:
    populated = [brief for brief in briefs if brief.items]
    if not populated:
        return "이번 주는 수집된 양자 분야 주요 이슈를 안전하게 정리하는 데 필요한 대표 스토리가 충분하지 않았습니다."
    lead = populated[0].lead_summary.strip()
    return lead or "이번 주 양자 분야의 핵심 흐름과 다음 관전 포인트를 정리했습니다."


def _build_segments(briefs: list[CategoryBrief]) -> list[dict[str, Any]]:
    return [
        {
            "category_key": brief.category_key,
            "category_label": brief.category_label,
            "lead_summary": brief.lead_summary,
            "item_count": len(brief.items),
            "items": [item.to_dict() for item in brief.items],
        }
        for brief in briefs
    ]


def _cluster_payload(cluster: StoryCluster) -> dict[str, Any]:
    representative = cluster.representative.raw
    return {
        "cluster_id": cluster.cluster_id,
        "headline": representative.title,
        "source": representative.source_label,
        "section_key": representative.section_key,
        "published_at": representative.published_at.isoformat() if representative.published_at else None,
        "excerpt": representative.excerpt,
        "site_brief_bullets": representative.site_brief_bullets[:3],
        "cluster_score": round(cluster.cluster_score, 3),
        "cluster_size": len(cluster.members),
        "source_labels": sorted({member.raw.source_label for member in cluster.members}),
        "canonical_url": representative.canonical_url,
    }


class WeeklyGeminiStudio:
    def __init__(self, config: WeeklyQuantumConfig) -> None:
        if not config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required for WeeklyGeminiStudio.")
        self.config = config
        self.client = genai.Client(api_key=config.gemini_api_key)

    def _generate_json(
        self,
        *,
        model: str,
        system_instruction: str,
        prompt: str,
        max_output_tokens: int,
        temperature: float,
    ) -> dict[str, Any]:
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                systemInstruction=system_instruction,
                temperature=temperature,
                maxOutputTokens=max_output_tokens,
                responseMimeType="application/json",
            ),
        )
        return _extract_json_payload(_extract_text(response))

    def create_category_brief(
        self,
        *,
        category_key: str,
        category_label: str,
        clusters: list[StoryCluster],
        max_story_count: int,
    ) -> CategoryBrief:
        payload = self._generate_json(
            model=self.config.triage_model,
            system_instruction=(
                "You are a careful Korean editor for a weekly quantum-industry radio briefing. "
                "Use only the supplied structured metadata. "
                "Do not invent facts, quotes, figures, causal claims, or market implications. "
                "If the metadata is thin, say so plainly and keep the wording compact."
            ),
            prompt=(
                f"Category: {category_label} ({category_key})\n"
                "Return exactly one JSON object.\n\n"
                "Required JSON shape:\n"
                "{\n"
                '  "lead_summary": "1-2 Korean sentences",\n'
                '  "items": [\n'
                "    {\n"
                '      "cluster_id": "string",\n'
                '      "headline": "string",\n'
                '      "summary": "1-2 Korean sentences",\n'
                '      "why_it_matters": "1 short Korean sentence",\n'
                '      "easy_explainer": "1 short Korean sentence with one easy analogy or plain-language explanation",\n'
                '      "confidence": "high|medium|low"\n'
                "    }\n"
                "  ]\n"
                "}\n\n"
                "Rules:\n"
                f"- Select up to {max_story_count} items.\n"
                "- Prefer higher-score clusters and broader cross-source coverage.\n"
                "- `lead_summary` must summarize the week's movement in this category, not list headlines.\n"
                "- `summary` should explain what changed using the excerpt/bullets only.\n"
                "- `why_it_matters` should be shorter than `summary`.\n"
                "- `easy_explainer` should make the topic easier for a non-expert with one light analogy or easy comparison.\n"
                "- Keep the `cluster_id` values from the input unchanged.\n"
                "- Never include URLs.\n\n"
                f"Clusters:\n{_json_dumps([_cluster_payload(cluster) for cluster in clusters])}"
            ),
            max_output_tokens=min(self.config.max_output_tokens, 2048),
            temperature=0.25,
        )

        cluster_by_id = {cluster.cluster_id: cluster for cluster in clusters}
        cluster_by_headline = {cluster.representative.raw.title: cluster for cluster in clusters}
        used_ids: set[str] = set()
        items: list[BriefItem] = []
        for raw_item in list(payload.get("items", []))[:max_story_count]:
            cluster_id = str(raw_item.get("cluster_id", "")).strip()
            headline = str(raw_item.get("headline", "")).strip()
            cluster = cluster_by_id.get(cluster_id) or cluster_by_headline.get(headline)
            if cluster is None or cluster.cluster_id in used_ids:
                continue
            representative = cluster.representative.raw
            items.append(
                BriefItem(
                    headline=headline or representative.title,
                    summary=str(raw_item.get("summary", "")).strip(),
                    why_it_matters=str(raw_item.get("why_it_matters", "")).strip(),
                    sources=sorted({member.raw.source_label for member in cluster.members}),
                    cluster_id=cluster.cluster_id,
                    easy_explainer=str(raw_item.get("easy_explainer", "")).strip(),
                    confidence=str(raw_item.get("confidence", "medium")).strip() or "medium",
                )
            )
            used_ids.add(cluster.cluster_id)

        return CategoryBrief(
            category_key=category_key,
            category_label=category_label,
            items=items,
            lead_summary=str(payload.get("lead_summary", "")).strip(),
        )

    def create_weekly_show(
        self,
        *,
        briefs: list[CategoryBrief],
        window: CollectionWindow,
    ) -> WeeklyShow:
        payload = self._generate_json(
            model=self.config.editor_model,
            system_instruction=(
                "You write a Korean weekly radio script for two speakers. "
                "The host is bright, brisk, and easy to listen to. "
                "The analyst is lively, concise, and very good at making hard topics feel simple. "
                "Every dialogue line must begin with the exact speaker labels provided. "
                "Avoid hype and do not overstate thin evidence."
            ),
            prompt=(
                f"Time window: {window.start.isoformat()} ~ {window.end.isoformat()}\n"
                f"Host label: {self.config.host_name}:\n"
                f"Analyst label: {self.config.analyst_name}:\n"
                "Return exactly one JSON object.\n\n"
                "Required JSON shape:\n"
                "{\n"
                '  "show_title": "string",\n'
                '  "show_summary": "1-2 Korean sentences",\n'
                '  "opening": "1 Korean sentence",\n'
                '  "closing": "1 Korean sentence",\n'
                '  "full_script_markdown": "markdown string with dialogue only",\n'
                '  "headline_script_text": "plain text dialogue for short headline-only audio"\n'
                "}\n\n"
                "Rules:\n"
                "- `full_script_markdown` must contain dialogue only, no headings or bullet lists.\n"
                f"- Every spoken line in `full_script_markdown` must start with `{self.config.host_name}:` or `{self.config.analyst_name}:`.\n"
                f"- Every spoken line in `headline_script_text` must start with `{self.config.host_name}:`.\n"
                "- Start with one short greeting and move straight into the first topic.\n"
                "- Do not introduce the speakers by name or explain the format.\n"
                "- Use short, natural turn-taking and avoid long monologues.\n"
                "- Cover each populated category once and avoid repeating the same story in multiple segments.\n"
                "- For each covered story, include one short easy analogy or plain-language explanation.\n"
                "- Keep the energy bright and light, but still informative.\n"
                "- Mention uncertainty plainly when details are still developing.\n"
                "- Do not include URLs.\n\n"
                f"Briefs:\n{_json_dumps([brief.to_dict() for brief in briefs])}"
            ),
            max_output_tokens=self.config.max_output_tokens + 1024,
            temperature=0.45,
        )

        full_script_markdown = str(payload.get("full_script_markdown", "")).strip()
        full_script_text = _markdown_to_plaintext(full_script_markdown)
        if not full_script_text:
            raise ValueError("Weekly show response did not contain a usable full script.")
        if f"{self.config.host_name}:" not in full_script_text or f"{self.config.analyst_name}:" not in full_script_text:
            raise ValueError("Weekly show script is missing required speaker labels.")
        for line in [line.strip() for line in full_script_text.splitlines() if line.strip()]:
            if not (
                line.startswith(f"{self.config.host_name}:")
                or line.startswith(f"{self.config.analyst_name}:")
            ):
                raise ValueError("Weekly show script contains a line without a valid speaker label.")

        headline_script_text = str(payload.get("headline_script_text", "")).strip()
        if not headline_script_text:
            raise ValueError("Weekly show response did not contain headline script text.")
        for line in [line.strip() for line in headline_script_text.splitlines() if line.strip()]:
            if not line.startswith(f"{self.config.host_name}:"):
                raise ValueError("Headline script contains a line without the host speaker label.")

        return WeeklyShow(
            window_start=window.start,
            window_end=window.end,
            host_name=self.config.host_name,
            analyst_name=self.config.analyst_name,
            show_title=str(payload.get("show_title", "")).strip() or _default_show_title(window),
            show_summary=str(payload.get("show_summary", "")).strip() or _default_show_summary(briefs),
            opening=str(payload.get("opening", "")).strip() or next(
                (line for line in full_script_text.splitlines() if line.strip()),
                "",
            ),
            segments=_build_segments(briefs),
            closing=str(payload.get("closing", "")).strip() or next(
                (line for line in reversed(full_script_text.splitlines()) if line.strip()),
                "",
            ),
            headline_script_text=headline_script_text,
            full_script_text=full_script_text,
            full_script_markdown=full_script_markdown,
        )

    def generate_audio(self, script_text: str) -> tuple[bytes, str]:
        attempts = self.config.tts_retry_count + 1
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                return self._generate_audio_once(script_text)
            except errors.ClientError as exc:
                last_error = exc
                status_code = getattr(exc, "status_code", None)
                is_retryable = status_code == 429 or "429" in str(exc)
                if attempt >= attempts - 1 or not is_retryable:
                    raise
                time.sleep(_retry_delay_seconds(str(exc), self.config.tts_retry_delay_seconds))
            except ValueError as exc:
                last_error = exc
                if attempt >= attempts - 1:
                    raise
                time.sleep(2)
        raise ValueError(f"Gemini TTS failed after retries: {last_error}")

    def _generate_audio_once(self, script_text: str) -> tuple[bytes, str]:
        response = self.client.models.generate_content(
            model=self.config.tts_model,
            contents=self._build_tts_prompt(script_text),
            config=types.GenerateContentConfig(
                responseModalities=["AUDIO"],
                speechConfig=types.SpeechConfig(
                    languageCode="ko-KR",
                    multiSpeakerVoiceConfig=types.MultiSpeakerVoiceConfig(
                        speakerVoiceConfigs=[
                            types.SpeakerVoiceConfig(
                                speaker=self.config.host_name,
                                voiceConfig=types.VoiceConfig(
                                    prebuiltVoiceConfig=types.PrebuiltVoiceConfig(
                                        voiceName=self.config.host_voice,
                                    ),
                                ),
                            ),
                            types.SpeakerVoiceConfig(
                                speaker=self.config.analyst_name,
                                voiceConfig=types.VoiceConfig(
                                    prebuiltVoiceConfig=types.PrebuiltVoiceConfig(
                                        voiceName=self.config.analyst_voice,
                                    ),
                                ),
                            ),
                        ],
                    ),
                ),
            ),
        )

        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            for part in getattr(content, "parts", []) or []:
                inline_data = getattr(part, "inline_data", None)
                if inline_data and getattr(inline_data, "data", None):
                    return inline_data.data, inline_data.mime_type or "audio/wav"

        raise ValueError("Gemini TTS response did not contain audio data.")

    def _build_tts_prompt(self, script_text: str) -> str:
        transcript = _format_tts_transcript(script_text, self.config.tts_turn_pause_multiplier)
        return (
            "# Korean Weekly Quantum Radio TTS\n"
            "Generate audio only for the transcript below.\n"
            "Do not add narration, labels, or explanations outside the transcript.\n"
            "Blank lines indicate silent handoff beats and must not be spoken.\n\n"
            "## Audio Profile\n"
            f"- {self.config.host_name}: a bright, friendly weekly-news host with clear pacing.\n"
            f"- {self.config.analyst_name}: a lively analyst with warm energy and easy explanations.\n\n"
            "## Director Notes\n"
            f"- Deliver at about {self.config.tts_speed_multiplier:.2f}x standard Korean radio pace.\n"
            f"- After each speaker change, leave a pause around {self.config.tts_turn_pause_multiplier:.2f}x a normal handoff.\n"
            "- Keep diction clear, natural, slightly upbeat, and never rushed.\n"
            "- Read every line exactly as written in Korean.\n\n"
            "## Transcript\n"
            f"{transcript}"
        )
