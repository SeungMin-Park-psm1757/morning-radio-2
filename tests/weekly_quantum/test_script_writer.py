from morning_radio.weekly_quantum.models import BriefItem, CategoryBrief
from morning_radio.weekly_quantum.script_writer import build_full_script

from .conftest import make_config


def test_build_full_script_uses_short_greeting_and_easy_explainer():
    config = make_config()
    briefs = [
        CategoryBrief(
            category_key="research_technology",
            category_label="연구와 기술",
            lead_summary="이번 주에는 실험과 하드웨어 개선 흐름이 산뜻하게 이어졌습니다.",
            items=[
                BriefItem(
                    headline="Neutral atom roadmap expands",
                    summary="하드웨어 선택지가 넓어지면서 기술 로드맵이 더 입체적으로 보이기 시작했습니다.",
                    why_it_matters="한 가지 방식에만 기대지 않는 개발 흐름을 확인하게 합니다.",
                    sources=["Quantum Insider"],
                    cluster_id="global-001",
                    easy_explainer="쉽게 보면 한 대의 엔진만 쓰던 차에, 상황별로 바꿔 쓸 수 있는 새 엔진을 하나 더 단 셈입니다.",
                )
            ],
        )
    ]

    script = build_full_script(briefs, config)

    assert script.splitlines()[0] == "진행자: 좋은 아침입니다. 이번 주 양자 흐름 바로 들어가볼게요."
    assert "어렵지 않게 비유하면 어떻게 이해하면 좋을까요?" in script
    assert "쉽게 보면 한 대의 엔진만 쓰던 차에" in script
    assert "정리해보겠습니다" not in script
