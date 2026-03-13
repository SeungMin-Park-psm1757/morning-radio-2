from __future__ import annotations

from .config import WeeklyQuantumConfig
from .models import CategoryBrief, WeeklyShow
from .window import CollectionWindow


def build_weekly_show(
    briefs: list[CategoryBrief],
    config: WeeklyQuantumConfig,
    window: CollectionWindow,
) -> WeeklyShow:
    opening = "안녕하세요. 이번 주 양자기술 아침 브리핑입니다."
    closing = "이상으로 이번 주 양자기술 브리핑을 마칩니다."
    full_script = build_full_script(briefs, config)
    headline_script = build_headlines_script(briefs, config)
    segments = [
        {
            "category_key": brief.category_key,
            "category_label": brief.category_label,
            "lead_summary": brief.lead_summary,
            "item_count": len(brief.items),
            "items": [item.to_dict() for item in brief.items],
        }
        for brief in briefs
    ]
    return WeeklyShow(
        window_start=window.start,
        window_end=window.end,
        host_name=config.host_name,
        analyst_name=config.analyst_name,
        opening=opening,
        segments=segments,
        closing=closing,
        headline_script_text=headline_script,
        full_script_text=full_script,
    )


def build_full_script(briefs: list[CategoryBrief], config: WeeklyQuantumConfig) -> str:
    lines: list[str] = []
    lines.append(f"{config.host_name}: 안녕하세요. 이번 주 양자기술 아침 브리핑입니다.")
    lines.append("")
    lines.append(f"{config.analyst_name}: 지난주 흐름을 큰 줄기부터 빠르게 정리해드릴게요.")
    lines.append("")

    for brief in briefs:
        if brief.items:
            lines.append(f"{config.host_name}: 먼저 {brief.category_label} 흐름부터 보겠습니다.")
            lines.append("")
            lines.append(f"{config.analyst_name}: {brief.lead_summary}")
            lines.append("")
        for item in brief.items:
            lines.append(f"{config.host_name}: 첫 소식입니다. {item.headline}")
            lines.append("")
            lines.append(f"{config.analyst_name}: {item.summary}")
            lines.append("")
            lines.append(f"{config.host_name}: 왜 중요한지 짚어보면, {item.why_it_matters}")
            lines.append("")

    if not any(brief.items for brief in briefs):
        lines.append(f"{config.host_name}: 이번 주는 아직 확정된 대표 스토리를 추리는 중입니다.")
        lines.append("")
        lines.append(f"{config.analyst_name}: 수집기와 요약 단계를 채워 넣으면 다음 실행부터 실제 주간 쇼 형태로 이어갈 수 있습니다.")
        lines.append("")

    lines.append(f"{config.host_name}: 이상으로 이번 주 양자기술 브리핑을 마칩니다.")
    return "\n".join(lines).strip()


def build_headlines_script(briefs: list[CategoryBrief], config: WeeklyQuantumConfig) -> str:
    lines: list[str] = [f"{config.host_name}: 이번 주 양자기술 헤드라인입니다.", ""]
    emitted = 0
    for brief in briefs:
        for item in brief.items[:6]:
            lines.append(f"{config.host_name}: {item.headline}")
            lines.append("")
            emitted += 1
    if emitted == 0:
        lines.append(f"{config.host_name}: 이번 주는 아직 헤드라인으로 확정된 스토리가 없습니다.")
    return "\n".join(lines).strip()


def render_weekly_script_markdown(show: WeeklyShow) -> str:
    title = f"# 주간 양자기술 라디오 ({show.window_end.strftime('%Y-%m-%d')})"
    return "\n".join([title, "", show.full_script_text]).strip() + "\n"


def build_message_digest(briefs: list[CategoryBrief], show: WeeklyShow) -> str:
    lines = [
        "# 주간 양자기술 다이제스트",
        "",
        f"- 기간: {show.window_start.isoformat()} ~ {show.window_end.isoformat()}",
    ]
    for brief in briefs:
        lines.append("")
        lines.append(f"## {brief.category_label}")
        if not brief.items:
            lines.append("- 이번 실행에서는 대표 스토리를 확보하지 못했습니다.")
            continue
        for item in brief.items:
            lines.append(f"- **{item.headline}**")
            lines.append(f"  요약: {item.summary}")
            lines.append(f"  왜 중요하나: {item.why_it_matters}")
    return "\n".join(lines).strip() + "\n"
