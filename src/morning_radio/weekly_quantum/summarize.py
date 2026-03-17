from __future__ import annotations

from dataclasses import dataclass

from .config import WeeklyQuantumConfig
from .gemini import WeeklyGeminiStudio
from .models import BriefItem, CategoryBrief, StoryCluster


@dataclass(frozen=True, slots=True)
class CategorySpec:
    key: str
    label: str
    max_items: int


_CATEGORY_SPECS: tuple[CategorySpec, ...] = (
    CategorySpec("industry_business", "산업과 투자", 4),
    CategorySpec("research_technology", "연구와 기술", 4),
    CategorySpec("policy_ecosystem", "정책과 생태계", 3),
    CategorySpec("analysis_outlook", "해설과 관전 포인트", 3),
)

_CATEGORY_BY_KEY = {spec.key: spec for spec in _CATEGORY_SPECS}


def categorize_cluster(cluster: StoryCluster) -> CategorySpec:
    raw = cluster.representative.raw
    source_key = raw.source_key.casefold()
    section_key = raw.section_key.casefold()
    text = " ".join([raw.title, raw.excerpt, " ".join(raw.tags)]).casefold()

    if source_key in {"qcr_qnalysis", "tqi_insights"} or any(term in text for term in ("analysis", "outlook", "insight")):
        return _CATEGORY_BY_KEY["analysis_outlook"]
    if source_key in {"tqi_national", "tqi_education"} or any(
        term in text for term in ("policy", "government", "defense", "education", "regulation", "standard")
    ):
        return _CATEGORY_BY_KEY["policy_ecosystem"]
    if source_key in {"physorg_quantum", "quantumzeitgeist_research", "quantumfrontiers_news", "tqi_research"} or any(
        term in text for term in ("research", "physics", "qubit", "algorithm", "error correction", "experiment")
    ):
        return _CATEGORY_BY_KEY["research_technology"]
    if source_key in {"tqi_business", "qcr_news", "qcr_our_take"} or any(
        term in text for term in ("business", "market", "funding", "company", "startup", "enterprise", "partnership")
    ):
        return _CATEGORY_BY_KEY["industry_business"]
    if "news" in section_key or "daily" in section_key:
        return _CATEGORY_BY_KEY["industry_business"]
    return _CATEGORY_BY_KEY["research_technology"]


def group_clusters_by_category(clusters: list[StoryCluster]) -> list[tuple[CategorySpec, list[StoryCluster]]]:
    grouped: dict[str, list[StoryCluster]] = {spec.key: [] for spec in _CATEGORY_SPECS}
    for cluster in clusters:
        grouped[categorize_cluster(cluster).key].append(cluster)
    return [(spec, grouped[spec.key]) for spec in _CATEGORY_SPECS if grouped[spec.key]]


def _cluster_confidence(cluster: StoryCluster) -> str:
    representative = cluster.representative.raw
    if representative.published_at and len({member.raw.source_key for member in cluster.members}) >= 2:
        return "high"
    if representative.published_at or representative.excerpt or representative.site_brief_bullets:
        return "medium"
    return "low"


def _story_summary(cluster: StoryCluster) -> str:
    representative = cluster.representative.raw
    if representative.site_brief_bullets:
        return representative.site_brief_bullets[0].strip()
    if representative.excerpt:
        return representative.excerpt.strip()
    return representative.title.strip()


def _why_it_matters(cluster: StoryCluster, spec: CategorySpec) -> str:
    if spec.key == "industry_business":
        return "상용화 속도와 기업 간 경쟁 구도를 읽는 데 필요한 흐름입니다."
    if spec.key == "research_technology":
        return "실험 성과가 실제 기술 로드맵으로 이어질 수 있는지 가늠하게 합니다."
    if spec.key == "policy_ecosystem":
        return "예산과 제도, 인력 생태계가 시장 속도를 어떻게 바꾸는지 보여줍니다."
    return "당장 큰 숫자보다도 다음 주 해석 프레임을 정리하는 데 도움이 됩니다."


def _lead_summary(spec: CategorySpec, items: list[BriefItem]) -> str:
    if not items:
        return f"이번 주 {spec.label}에서는 방송에 넣을 만한 대표 스토리가 충분하지 않았습니다."
    if spec.key == "industry_business":
        return f"이번 주 {spec.label}에서는 기업 발표와 사업화 움직임을 중심으로 {len(items)}개의 대표 흐름이 포착됐습니다."
    if spec.key == "research_technology":
        return f"이번 주 {spec.label}에서는 실험 결과와 기술 진전이 함께 이어지며 {len(items)}개의 핵심 이슈가 남았습니다."
    if spec.key == "policy_ecosystem":
        return f"이번 주 {spec.label}에서는 제도, 예산, 인력 기반과 연결된 {len(items)}개의 흐름이 눈에 띄었습니다."
    return f"이번 주 {spec.label}에서는 해석이 필요한 신호와 관전 포인트가 {len(items)}건으로 압축됐습니다."


def _heuristic_brief(spec: CategorySpec, clusters: list[StoryCluster]) -> CategoryBrief:
    items: list[BriefItem] = []
    for cluster in clusters[: spec.max_items]:
        representative = cluster.representative.raw
        items.append(
            BriefItem(
                headline=representative.title,
                summary=_story_summary(cluster),
                why_it_matters=_why_it_matters(cluster, spec),
                sources=sorted({member.raw.source_label for member in cluster.members}),
                cluster_id=cluster.cluster_id,
                confidence=_cluster_confidence(cluster),
            )
        )
    return CategoryBrief(
        category_key=spec.key,
        category_label=spec.label,
        items=items,
        lead_summary=_lead_summary(spec, items),
    )


def heuristic_briefs(clusters: list[StoryCluster]) -> list[CategoryBrief]:
    grouped = group_clusters_by_category(clusters)
    if not grouped:
        return [
            CategoryBrief(
                category_key="weekly_quantum",
                category_label="주간 양자 브리핑",
                items=[],
                lead_summary="이번 주는 대표 스토리가 충분히 수집되지 않아 보수적인 요약만 남겼습니다.",
            )
        ]
    return [_heuristic_brief(spec, grouped_clusters) for spec, grouped_clusters in grouped]


def build_category_briefs(
    *,
    clusters: list[StoryCluster],
    config: WeeklyQuantumConfig,
    editor: WeeklyGeminiStudio | None = None,
) -> tuple[list[CategoryBrief], list[str]]:
    grouped = group_clusters_by_category(clusters)
    if not grouped:
        return heuristic_briefs([]), []

    briefs: list[CategoryBrief] = []
    degraded_modes: list[str] = []
    for spec, grouped_clusters in grouped:
        if editor is None or not config.llm_enabled:
            briefs.append(_heuristic_brief(spec, grouped_clusters))
            continue

        try:
            brief = editor.create_category_brief(
                category_key=spec.key,
                category_label=spec.label,
                clusters=grouped_clusters[: spec.max_items],
                max_story_count=spec.max_items,
            )
            if not brief.items or not brief.lead_summary.strip():
                raise ValueError("LLM brief response was empty.")
            briefs.append(brief)
        except Exception:
            briefs.append(_heuristic_brief(spec, grouped_clusters))
            degraded_modes.append(f"brief_fallback_{spec.key}")
    return briefs, degraded_modes
