from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from .config import WeeklyQuantumConfig
from .dedup import cluster_articles, exact_dedup
from .models import WeeklyRunState
from .normalize import normalize_article
from .ranking import score_article, score_cluster
from .script_writer import build_full_script, build_headlines_script
from .state_store import load_run_state, save_run_state
from .summarize import heuristic_briefs
from .window import determine_collection_window


def run_weekly_quantum_pipeline(config: WeeklyQuantumConfig, *, now: datetime | None = None) -> Path:
    """Starter pipeline scaffold.

    This intentionally does not implement networked collection.
    It provides the execution skeleton Codex can fill in safely.
    """
    current = now or datetime.now(tz=UTC)
    state = load_run_state(config.state_path)
    window = determine_collection_window(now=current, state=state, config=config)

    run_dir = config.output_dir / current.astimezone(UTC).strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    # TODO: replace with real collector orchestration
    raw_items = []
    normalized = [normalize_article(item) for item in raw_items]
    for item in normalized:
        score_article(item, now=current)

    deduped = exact_dedup(normalized)
    clusters = cluster_articles(deduped)
    for cluster in clusters:
        score_cluster(cluster)

    clusters = sorted(clusters, key=lambda cluster: cluster.cluster_score, reverse=True)
    briefs = heuristic_briefs(clusters)
    full_script = build_full_script(briefs, config)
    headlines_script = build_headlines_script(briefs, config)

    (run_dir / "weekly_script.txt").write_text(full_script, encoding="utf-8")
    (run_dir / "weekly_headlines.txt").write_text(headlines_script, encoding="utf-8")
    (run_dir / "message_digest.md").write_text(full_script, encoding="utf-8")
    (run_dir / "summary.md").write_text(
        "\n".join(
            [
                "# Weekly Quantum Summary",
                "",
                f"- window_start: {window.start.isoformat()}",
                f"- window_end: {window.end.isoformat()}",
                f"- bootstrap: {window.bootstrap}",
                f"- raw_items: {len(raw_items)}",
                f"- clusters: {len(clusters)}",
                "",
                "This is a scaffold run. Replace with real collectors and generation.",
            ]
        ),
        encoding="utf-8",
    )

    (run_dir / "run_metadata.json").write_text(
        json.dumps(
            {
                "window_start": window.start.isoformat(),
                "window_end": window.end.isoformat(),
                "bootstrap": window.bootstrap,
                "raw_items": len(raw_items),
                "clusters": len(clusters),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    new_state = WeeklyRunState(
        last_attempt_started_at=current,
        last_successful_window_end=window.end,
        last_successful_run_dir=str(run_dir),
        last_delivery_status="scaffold_only",
        last_source_health=[],
    )
    save_run_state(config.state_path, new_state)
    return run_dir
