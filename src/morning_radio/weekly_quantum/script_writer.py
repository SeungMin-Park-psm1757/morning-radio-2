from __future__ import annotations

from .config import WeeklyQuantumConfig
from .models import CategoryBrief, WeeklyShow
from .window import CollectionWindow


def _show_title(window: CollectionWindow) -> str:
    return f"주간 양자 브리핑 ({window.end.date().isoformat()})"


def _show_summary(briefs: list[CategoryBrief]) -> str:
    populated = [brief for brief in briefs if brief.items]
    if not populated:
        return "이번 주는 확정적으로 묶을 수 있는 대표 스토리가 많지 않아 보수적인 템플릿 브리핑으로 정리했습니다."
    labels = ", ".join(brief.category_label for brief in populated[:3])
    return f"이번 주 양자 분야에서는 {labels} 흐름을 중심으로 핵심 이슈를 추려 봤습니다."


def build_weekly_show(
    briefs: list[CategoryBrief],
    config: WeeklyQuantumConfig,
    window: CollectionWindow,
) -> WeeklyShow:
    full_script = build_full_script(briefs, config)
    headline_script = build_headlines_script(briefs, config)
    opening = next((line for line in full_script.splitlines() if line.strip()), "")
    closing = next((line for line in reversed(full_script.splitlines()) if line.strip()), "")
    return WeeklyShow(
        window_start=window.start,
        window_end=window.end,
        host_name=config.host_name,
        analyst_name=config.analyst_name,
        show_title=_show_title(window),
        show_summary=_show_summary(briefs),
        opening=opening,
        segments=[
            {
                "category_key": brief.category_key,
                "category_label": brief.category_label,
                "lead_summary": brief.lead_summary,
                "item_count": len(brief.items),
                "items": [item.to_dict() for item in brief.items],
            }
            for brief in briefs
        ],
        closing=closing,
        headline_script_text=headline_script,
        full_script_text=full_script,
        full_script_markdown=full_script,
    )


def build_full_script(briefs: list[CategoryBrief], config: WeeklyQuantumConfig) -> str:
    lines: list[str] = [
        f"{config.host_name}: 좋은 아침입니다. 이번 주 양자 흐름 바로 들어가볼게요.",
        "",
        f"{config.analyst_name}: 좋아요. 이번 주에도 재미있게 풀어볼 만한 포인트만 경쾌하게 골라왔습니다.",
        "",
    ]

    emitted = 0
    for brief in briefs:
        if not brief.items:
            continue
        lines.append(f"{config.host_name}: 먼저 {brief.category_label} 흐름부터 가볍게 짚어볼까요?")
        lines.append("")
        lines.append(f"{config.analyst_name}: {brief.lead_summary}")
        lines.append("")
        for item in brief.items:
            lines.append(f"{config.host_name}: 이번 주에 특히 눈에 띈 이슈는 {item.headline}입니다.")
            lines.append("")
            lines.append(f"{config.analyst_name}: {item.summary}")
            lines.append("")
            lines.append(f"{config.host_name}: 여기서 우리가 꼭 봐야 할 포인트는 뭘까요?")
            lines.append("")
            lines.append(f"{config.analyst_name}: {item.why_it_matters}")
            lines.append("")
            lines.append(f"{config.host_name}: 어렵지 않게 비유하면 어떻게 이해하면 좋을까요?")
            lines.append("")
            lines.append(f"{config.analyst_name}: {item.easy_explainer}")
            lines.append("")
            emitted += 1

    if emitted == 0:
        lines.extend(
            [
                f"{config.host_name}: 이번 주는 아직 대표 스토리를 강하게 묶을 만큼 신호가 충분하진 않았습니다.",
                "",
                f"{config.analyst_name}: 그래도 수집 흐름은 살아 있으니, 다음 실행에서는 더 선명한 주간본으로 바로 이어갈 수 있습니다.",
                "",
            ]
        )

    lines.append(f"{config.host_name}: 오늘 브리핑은 여기까지입니다. 다음 주에도 핵심만 산뜻하게 가져올게요.")
    return "\n".join(lines).strip()


def build_headlines_script(briefs: list[CategoryBrief], config: WeeklyQuantumConfig) -> str:
    lines: list[str] = [
        f"{config.host_name}: 좋은 아침입니다. 이번 주 양자 헤드라인 바로 짚어볼게요.",
        "",
    ]
    emitted = 0
    for brief in briefs:
        for item in brief.items[:2]:
            lines.append(f"{config.host_name}: {item.headline}")
            lines.append("")
            emitted += 1
    if emitted == 0:
        lines.append(f"{config.host_name}: 이번 주는 헤드라인으로 압축할 대표 스토리가 아직 충분하지 않습니다.")
    return "\n".join(lines).strip()


def render_weekly_script_markdown(show: WeeklyShow) -> str:
    lines = [
        f"# {show.show_title}",
        "",
        show.show_summary,
        "",
        show.full_script_markdown.strip() or show.full_script_text.strip(),
    ]
    return "\n".join(line for line in lines if line is not None).strip() + "\n"


def build_message_digest(briefs: list[CategoryBrief], show: WeeklyShow) -> str:
    lines = [
        f"# {show.show_title}",
        "",
        f"- 기간: {show.window_start.isoformat()} ~ {show.window_end.isoformat()}",
        f"- 요약: {show.show_summary}",
    ]
    for brief in briefs:
        lines.append("")
        lines.append(f"## {brief.category_label}")
        if not brief.items:
            lines.append("- 이번 실행에서는 대표 스토리가 충분하지 않았습니다.")
            continue
        for item in brief.items:
            lines.append(f"- **{item.headline}**")
            lines.append(f"  요약: {item.summary}")
            lines.append(f"  왜 중요한가: {item.why_it_matters}")
    return "\n".join(lines).strip() + "\n"
