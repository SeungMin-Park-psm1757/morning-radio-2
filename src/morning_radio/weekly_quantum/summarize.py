from __future__ import annotations

from .models import BriefItem, CategoryBrief, StoryCluster


def heuristic_briefs(clusters: list[StoryCluster]) -> list[CategoryBrief]:
    """Fallback brief generator when LLM is skipped or unavailable."""
    items: list[BriefItem] = []
    for cluster in clusters[:8]:
        rep = cluster.representative.raw
        summary = rep.excerpt or (rep.site_brief_bullets[0] if rep.site_brief_bullets else rep.title)
        items.append(
            BriefItem(
                headline=rep.title,
                summary=summary,
                why_it_matters="이번 주 양자기술 흐름에서 눈여겨볼 대표 이슈입니다.",
                sources=sorted({member.raw.source_label for member in cluster.members}),
                cluster_id=cluster.cluster_id,
                confidence="medium" if rep.published_at else "low",
            )
        )

    lead_summary = (
        "한 주간의 핵심 양자기술 동향을 정리했습니다."
        if items
        else "이번 실행에서는 주간 브리핑에 넣을 확정 스토리를 아직 확보하지 못했습니다."
    )
    return [
        CategoryBrief(
            category_key="weekly_quantum",
            category_label="주간 양자기술",
            items=items,
            lead_summary=lead_summary,
        )
    ]
