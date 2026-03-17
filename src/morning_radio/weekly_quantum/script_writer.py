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
    opening = f"{config.host_name}: 안녕하세요. 이번 주 양자 브리핑을 정리해보겠습니다."
    closing = f"{config.host_name}: 여기까지 이번 주 양자 브리핑이었습니다."
    full_script = build_full_script(briefs, config)
    headline_script = build_headlines_script(briefs, config)
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
        f"{config.host_name}: 안녕하세요. 이번 주 양자 기술 흐름을 짚어보겠습니다.",
        "",
        f"{config.analyst_name}: 산업과 연구, 정책 신호까지 한 번에 정리해드리겠습니다.",
        "",
    ]

    emitted = 0
    for brief in briefs:
        if not brief.items:
            continue
        lines.append(f"{config.host_name}: 먼저 {brief.category_label} 흐름부터 보겠습니다.")
        lines.append("")
        lines.append(f"{config.analyst_name}: {brief.lead_summary}")
        lines.append("")
        for item in brief.items:
            lines.append(f"{config.host_name}: 이번 주에 눈에 띈 이슈는 {item.headline}입니다.")
            lines.append("")
            lines.append(f"{config.analyst_name}: {item.summary}")
            lines.append("")
            lines.append(f"{config.host_name}: 이 대목은 왜 중요할까요?")
            lines.append("")
            lines.append(f"{config.analyst_name}: {item.why_it_matters}")
            lines.append("")
            emitted += 1

    if emitted == 0:
        lines.extend(
            [
                f"{config.host_name}: 이번 주는 아직 대표 스토리를 강하게 묶기 어려운 상황입니다.",
                "",
                f"{config.analyst_name}: 수집과 요약 경로는 유지한 채, 다음 실행에서 더 완성도 높은 주간본으로 이어가겠습니다.",
                "",
            ]
        )

    lines.append(f"{config.host_name}: 여기까지 이번 주 양자 브리핑이었습니다.")
    return "\n".join(lines).strip()


def build_headlines_script(briefs: list[CategoryBrief], config: WeeklyQuantumConfig) -> str:
    lines: list[str] = [
        f"{config.host_name}: 이번 주 양자 분야 헤드라인입니다.",
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
