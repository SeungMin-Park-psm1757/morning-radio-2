from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from .audio import write_audio_output
from .collectors import PhysOrgCollector, QCRCollector, QuantumFrontiersCollector, QuantumZeitgeistCollector, TQICollector
from .collectors.base import SourceConfig
from .config import WeeklyQuantumConfig, build_source_configs
from .dedup import cluster_articles, exact_dedup
from .delivery import deliver_weekly_bundle, public_links_for_run
from .gemini import WeeklyGeminiStudio
from .models import CategoryBrief, DeliveryResult, RawArticle, SourceHealth, StoryCluster, WeeklyRunState, WeeklyShow
from .normalize import normalize_article
from .ranking import score_article, score_cluster, select_top_clusters
from .script_writer import build_message_digest, build_weekly_show, render_weekly_script_markdown
from .state_store import load_run_state, save_run_state
from .summarize import build_category_briefs
from .window import CollectionWindow, determine_collection_window


class _CollectorProtocol(Protocol):
    def collect(self, config: SourceConfig): ...


_COLLECTOR_REGISTRY: dict[str, type[_CollectorProtocol]] = {
    "tqi": TQICollector,
    "physorg": PhysOrgCollector,
    "quantumzeitgeist": QuantumZeitgeistCollector,
    "qcr": QCRCollector,
    "quantumfrontiers": QuantumFrontiersCollector,
}


def run_weekly_quantum_pipeline(config: WeeklyQuantumConfig, *, now: datetime | None = None) -> Path:
    current = now or datetime.now(tz=UTC)
    state = load_run_state(config.state_path)
    window = determine_collection_window(now=current, state=state, config=config)

    run_dir = config.output_dir / current.astimezone(UTC).strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    source_configs = build_source_configs(config.max_list_items_per_source)
    raw_items, source_health = _collect_sources(
        source_configs,
        timeout_seconds=config.request_timeout_seconds,
        retry_count=config.retry_count,
    )
    windowed_raw_items = _filter_items_for_window(raw_items, window)
    _apply_window_counts(source_health, raw_items, windowed_raw_items)

    normalized = [normalize_article(item) for item in windowed_raw_items]
    for item in normalized:
        score_article(item, now=current)

    deduped = exact_dedup(normalized)
    clusters = cluster_articles(deduped)
    for cluster in clusters:
        score_cluster(cluster)
    selected_clusters = select_top_clusters(clusters, config.max_selected_stories)
    llm_clusters = selected_clusters[: config.llm_story_limit]

    degraded_modes = _degraded_modes(config, source_health)
    runtime_notes: list[str] = []

    editor: WeeklyGeminiStudio | None = None
    if config.llm_enabled or config.tts_enabled:
        try:
            editor = WeeklyGeminiStudio(config)
        except Exception as exc:
            runtime_notes.append(f"weekly_gemini_init:{exc}")
            degraded_modes.append("gemini_client_init_failed")

    briefs, brief_degraded = build_category_briefs(
        clusters=llm_clusters,
        config=config,
        editor=editor,
    )
    degraded_modes.extend(brief_degraded)

    weekly_show, script_degraded, script_notes = _generate_weekly_show(
        briefs=briefs,
        config=config,
        window=window,
        editor=editor,
    )
    degraded_modes.extend(script_degraded)
    runtime_notes.extend(script_notes)

    weekly_script_markdown = render_weekly_script_markdown(weekly_show)
    message_digest = build_message_digest(briefs, weekly_show)

    _write_json(run_dir / "raw_items.json", [item.to_dict() for item in raw_items])
    _write_json(run_dir / "normalized_items.json", [item.to_dict() for item in normalized])
    _write_json(run_dir / "clusters.json", [cluster.to_dict() for cluster in clusters])
    _write_json(
        run_dir / "selected_items.json",
        [cluster.representative.to_dict() for cluster in selected_clusters],
    )
    _write_json(run_dir / "category_briefs.json", [brief.to_dict() for brief in briefs])
    _write_json(run_dir / "weekly_show.json", weekly_show.to_dict())
    _write_json(run_dir / "source_health.json", [health.to_dict() for health in source_health])

    (run_dir / "weekly_script.md").write_text(weekly_script_markdown, encoding="utf-8")
    (run_dir / "weekly_script.txt").write_text(weekly_show.full_script_text + "\n", encoding="utf-8")
    (run_dir / "weekly_headlines.txt").write_text(weekly_show.headline_script_text + "\n", encoding="utf-8")
    (run_dir / "message_digest.md").write_text(message_digest, encoding="utf-8")

    full_audio_path: Path | None = None
    audio_metadata, audio_degraded, audio_notes = _generate_audio_outputs(
        config=config,
        editor=editor,
        run_dir=run_dir,
        full_script_text=weekly_show.full_script_text,
    )
    degraded_modes.extend(audio_degraded)
    runtime_notes.extend(audio_notes)
    if audio_metadata["full"]["generated"]:
        full_audio_path = run_dir / "weekly_full.mp3"

    delivery = DeliveryResult()
    if config.telegram_enabled:
        delivery = deliver_weekly_bundle(
            config=config,
            digest_markdown=message_digest,
            title=weekly_show.show_title,
            full_audio_path=full_audio_path,
            public_links=public_links_for_run(
                config=config,
                run_dir=run_dir,
                full_audio_path=full_audio_path,
            ),
        )
        degraded_modes.extend(_error_code(error) for error in delivery.errors)

    quota_log = _quota_log(config=config, selected_clusters=selected_clusters, briefs=briefs)
    degraded_modes = sorted(set(degraded_modes))

    summary = _build_summary(
        window=window,
        run_dir=run_dir,
        raw_items_count=len(raw_items),
        in_window_count=len(windowed_raw_items),
        normalized_count=len(normalized),
        clusters=clusters,
        selected_clusters=selected_clusters,
        source_health=source_health,
        degraded_modes=degraded_modes,
        delivery_status=delivery,
        weekly_show=weekly_show,
        audio_metadata=audio_metadata,
        quota_log=quota_log,
    )
    (run_dir / "summary.md").write_text(summary, encoding="utf-8")

    run_succeeded = any(health.success for health in source_health)
    should_advance_state = run_succeeded and not config.dry_run
    new_state = WeeklyRunState(
        last_attempt_started_at=current,
        last_successful_window_end=window.end if should_advance_state else state.last_successful_window_end,
        last_successful_run_dir=str(run_dir) if should_advance_state else state.last_successful_run_dir,
        last_delivery_status=_last_delivery_status(
            config=config,
            run_succeeded=run_succeeded,
            delivery=delivery,
            degraded_modes=degraded_modes,
        ),
        last_source_health=[health.to_dict() for health in source_health],
    )
    save_run_state(config.state_path, new_state)

    _write_json(
        run_dir / "run_metadata.json",
        {
            "version": "weekly-quantum-v2",
            "generated_at": current.isoformat(),
            "window": {
                "start": window.start.isoformat(),
                "end": window.end.isoformat(),
                "bootstrap": window.bootstrap,
                "manual_override": window.manual_override,
            },
            "config": config.to_safe_dict(),
            "counts": {
                "sources": len(source_configs),
                "raw_items": len(raw_items),
                "raw_items_in_window": len(windowed_raw_items),
                "normalized_items": len(normalized),
                "clusters": len(clusters),
                "selected_clusters": len(selected_clusters),
                "brief_clusters": len(llm_clusters),
                "brief_categories": len(briefs),
            },
            "quota_log": quota_log,
            "outputs": {
                "run_dir": str(run_dir),
                "weekly_script_md": str(run_dir / "weekly_script.md"),
                "weekly_script_txt": str(run_dir / "weekly_script.txt"),
                "weekly_headlines_txt": str(run_dir / "weekly_headlines.txt"),
                "message_digest_md": str(run_dir / "message_digest.md"),
                "source_health_json": str(run_dir / "source_health.json"),
                "summary_md": str(run_dir / "summary.md"),
                "weekly_full_mp3": str(full_audio_path) if full_audio_path else None,
            },
            "audio": audio_metadata,
            "delivery": delivery.to_dict(),
            "degraded_modes": degraded_modes,
            "runtime_notes": runtime_notes,
        },
    )
    return run_dir


def _collect_sources(
    source_configs: list[SourceConfig],
    *,
    timeout_seconds: int,
    retry_count: int,
) -> tuple[list[RawArticle], list[SourceHealth]]:
    raw_items: list[RawArticle] = []
    source_health: list[SourceHealth] = []

    for source_config in source_configs:
        collector_cls = _COLLECTOR_REGISTRY[source_config.kind]
        collector = collector_cls(timeout_seconds=timeout_seconds, retry_count=retry_count)
        result = collector.collect(source_config)
        raw_items.extend(result.items)
        if result.health is None:
            source_health.append(
                SourceHealth(
                    source_key=source_config.key,
                    requested=True,
                    success=False,
                    fallback_mode_used="missing_health",
                    error="Collector returned no source-health payload.",
                )
            )
        else:
            source_health.append(result.health)
    return raw_items, source_health


def _filter_items_for_window(raw_items: list[RawArticle], window: CollectionWindow) -> list[RawArticle]:
    filtered: list[RawArticle] = []
    for item in raw_items:
        if item.published_at is None:
            filtered.append(item)
            continue
        published_at = item.published_at.astimezone(UTC)
        if window.start <= published_at <= window.end:
            filtered.append(item)
    return filtered


def _apply_window_counts(
    source_health: list[SourceHealth],
    raw_items: list[RawArticle],
    windowed_raw_items: list[RawArticle],
) -> None:
    seen_counts: dict[str, int] = {}
    window_counts: dict[str, int] = {}
    for item in raw_items:
        seen_counts[item.source_key] = seen_counts.get(item.source_key, 0) + 1
    for item in windowed_raw_items:
        window_counts[item.source_key] = window_counts.get(item.source_key, 0) + 1
    for health in source_health:
        health.items_seen = seen_counts.get(health.source_key, 0)
        health.items_in_window = window_counts.get(health.source_key, 0)


def _generate_weekly_show(
    *,
    briefs: list[CategoryBrief],
    config: WeeklyQuantumConfig,
    window: CollectionWindow,
    editor: WeeklyGeminiStudio | None,
) -> tuple[WeeklyShow, list[str], list[str]]:
    if editor is None or not config.llm_enabled:
        return build_weekly_show(briefs, config, window), [], []

    try:
        return editor.create_weekly_show(briefs=briefs, window=window), [], []
    except Exception as exc:
        return build_weekly_show(briefs, config, window), ["script_fallback_template"], [f"weekly_show:{exc}"]


def _generate_audio_outputs(
    *,
    config: WeeklyQuantumConfig,
    editor: WeeklyGeminiStudio | None,
    run_dir: Path,
    full_script_text: str,
) -> tuple[dict[str, dict[str, Any]], list[str], list[str]]:
    metadata: dict[str, dict[str, Any]] = {
        "full": {"generated": False, "path": None},
    }
    degraded_modes: list[str] = []
    runtime_notes: list[str] = []

    if not config.tts_enabled:
        return metadata, degraded_modes, runtime_notes
    if editor is None:
        return metadata, ["tts_editor_unavailable"], ["tts:editor unavailable"]

    try:
        audio_bytes, mime_type = editor.generate_audio(full_script_text)
        full_path = write_audio_output(
            run_dir=run_dir,
            audio_bytes=audio_bytes,
            mime_type=mime_type,
            file_name="weekly_full.mp3",
            bitrate_kbps=config.tts_bitrate_kbps,
        )
        metadata["full"] = {
            "generated": True,
            "mime_type": mime_type,
            "path": full_path.name,
        }
    except Exception as exc:
        degraded_modes.append("tts_full_failed")
        metadata["full"]["error"] = str(exc)
        runtime_notes.append(f"tts_full:{exc}")

    return metadata, degraded_modes, runtime_notes


def _degraded_modes(config: WeeklyQuantumConfig, source_health: list[SourceHealth]) -> list[str]:
    degraded: list[str] = []
    if config.skip_llm or not config.llm_enabled:
        degraded.append("heuristic_briefs_only")
    if config.skip_tts:
        degraded.append("tts_skipped")
    elif config.enable_tts and not config.tts_enabled:
        degraded.append("tts_unavailable")
    if config.skip_telegram or config.dry_run:
        degraded.append("telegram_skipped")
    elif config.enable_telegram and not config.telegram_enabled:
        degraded.append("telegram_unavailable")
    if source_health and not any(health.success for health in source_health):
        degraded.append("no_successful_sources")
    return degraded


def _quota_log(
    *,
    config: WeeklyQuantumConfig,
    selected_clusters: list[StoryCluster],
    briefs: list[CategoryBrief],
) -> dict[str, Any]:
    return {
        "selected_clusters": len(selected_clusters),
        "llm_story_limit": config.llm_story_limit,
        "estimated_text_calls": (len(briefs) + 1) if config.llm_enabled else 0,
        "estimated_tts_calls": 1 if config.tts_enabled else 0,
    }


def _last_delivery_status(
    *,
    config: WeeklyQuantumConfig,
    run_succeeded: bool,
    delivery: DeliveryResult,
    degraded_modes: list[str],
) -> str:
    if config.dry_run:
        return "dry_run"
    if not run_succeeded:
        return "degraded"
    if delivery.errors or any(mode in degraded_modes for mode in ("tts_full_failed", "script_fallback_template")):
        return "degraded"
    if config.skip_telegram or config.skip_tts or config.skip_llm:
        return "skipped"
    return "ok"


def _error_code(error: str) -> str:
    return error.split(":", 1)[0].strip()


def _build_summary(
    *,
    window: CollectionWindow,
    run_dir: Path,
    raw_items_count: int,
    in_window_count: int,
    normalized_count: int,
    clusters: list[StoryCluster],
    selected_clusters: list[StoryCluster],
    source_health: list[SourceHealth],
    degraded_modes: list[str],
    delivery_status: DeliveryResult,
    weekly_show: WeeklyShow,
    audio_metadata: dict[str, dict[str, Any]],
    quota_log: dict[str, Any],
) -> str:
    lines = [
        "# Weekly Quantum Summary",
        "",
        f"- run_dir: {run_dir}",
        f"- title: {weekly_show.show_title}",
        f"- window_start: {window.start.isoformat()}",
        f"- window_end: {window.end.isoformat()}",
        f"- bootstrap: {window.bootstrap}",
        f"- manual_override: {window.manual_override}",
        f"- raw_items: {raw_items_count}",
        f"- items_in_window: {in_window_count}",
        f"- normalized_items: {normalized_count}",
        f"- clusters: {len(clusters)}",
        f"- selected_clusters: {len(selected_clusters)}",
        f"- estimated_text_calls: {quota_log['estimated_text_calls']}",
        f"- estimated_tts_calls: {quota_log['estimated_tts_calls']}",
        f"- full_audio_generated: {audio_metadata['full']['generated']}",
        f"- delivery_text_sent: {delivery_status.text_sent}",
        f"- delivery_full_audio_sent: {delivery_status.full_audio_sent}",
        f"- delivery_headlines_audio_sent: {delivery_status.headlines_audio_sent}",
        "",
        "## Degraded Modes",
    ]
    for item in degraded_modes or ["none"]:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("## Source Health")
    for health in source_health:
        error_text = health.error or "-"
        fallback_text = health.fallback_mode_used or "-"
        lines.append(
            f"- {health.source_key}: success={health.success}, items_seen={health.items_seen}, "
            f"items_in_window={health.items_in_window}, fallback={fallback_text}, error={error_text}"
        )

    return "\n".join(lines).strip() + "\n"


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
