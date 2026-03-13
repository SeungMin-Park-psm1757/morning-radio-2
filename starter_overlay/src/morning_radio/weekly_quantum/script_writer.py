from __future__ import annotations

from .config import WeeklyQuantumConfig
from .models import CategoryBrief


def build_full_script(briefs: list[CategoryBrief], config: WeeklyQuantumConfig) -> str:
    lines: list[str] = []
    lines.append(f"{config.host_name}: 안녕하세요. 이번 주 양자기술 아침 브리핑입니다.")
    lines.append("")
    lines.append(f"{config.analyst_name}: 지난주 흐름을 큰 줄기부터 빠르게 정리해드릴게요.")
    lines.append("")

    for brief in briefs:
        for item in brief.items:
            lines.append(f"{config.host_name}: 첫 소식입니다. {item.headline}")
            lines.append("")
            lines.append(f"{config.analyst_name}: {item.summary}")
            lines.append("")
            lines.append(f"{config.host_name}: 왜 중요한지 짚어보면, {item.why_it_matters}")
            lines.append("")

    lines.append(f"{config.host_name}: 이상으로 이번 주 양자기술 브리핑을 마칩니다.")
    return "\n".join(lines).strip()


def build_headlines_script(briefs: list[CategoryBrief], config: WeeklyQuantumConfig) -> str:
    lines: list[str] = [f"{config.host_name}: 이번 주 양자기술 헤드라인입니다.", ""]
    for brief in briefs:
        for item in brief.items[:6]:
            lines.append(f"- {item.headline}")
    return "\n".join(lines).strip()
