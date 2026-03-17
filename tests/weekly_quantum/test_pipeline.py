from datetime import UTC, datetime
from pathlib import Path

from morning_radio.weekly_quantum.models import BriefItem, CategoryBrief, RawArticle, SourceHealth, WeeklyShow
from morning_radio.weekly_quantum.pipeline import run_weekly_quantum_pipeline
from morning_radio.weekly_quantum.state_store import load_run_state

from .conftest import make_config


def test_pipeline_writes_weekly_outputs_and_does_not_advance_success_state(tmp_path: Path, monkeypatch):
    now = datetime(2026, 3, 16, 0, 0, tzinfo=UTC)
    config = make_config(
        output_dir=tmp_path / "output" / "weekly_quantum",
        state_path=tmp_path / "state" / "weekly_quantum_run_state.json",
        skip_llm=True,
        skip_tts=True,
        skip_telegram=True,
        dry_run=True,
    )
    monkeypatch.setattr(
        "morning_radio.weekly_quantum.pipeline._collect_sources",
        lambda *args, **kwargs: (
            [],
            [
                SourceHealth(
                    source_key="tqi_daily",
                    requested=True,
                    success=False,
                    fallback_mode_used="test_stub",
                    error="stubbed collector",
                )
            ],
        ),
    )

    run_dir = run_weekly_quantum_pipeline(config, now=now)

    expected_files = {
        "raw_items.json",
        "normalized_items.json",
        "clusters.json",
        "selected_items.json",
        "category_briefs.json",
        "weekly_show.json",
        "weekly_script.md",
        "weekly_script.txt",
        "weekly_headlines.txt",
        "message_digest.md",
        "source_health.json",
        "summary.md",
        "run_metadata.json",
    }
    assert expected_files <= {path.name for path in run_dir.iterdir()}

    state = load_run_state(config.state_path)
    assert state.last_attempt_started_at == now
    assert state.last_successful_window_end is None


def test_pipeline_dry_run_does_not_advance_success_window(tmp_path: Path, monkeypatch):
    now = datetime(2026, 3, 16, 0, 0, tzinfo=UTC)
    config = make_config(
        output_dir=tmp_path / "output" / "weekly_quantum",
        state_path=tmp_path / "state" / "weekly_quantum_run_state.json",
        dry_run=True,
        skip_telegram=True,
    )
    monkeypatch.setattr(
        "morning_radio.weekly_quantum.pipeline._collect_sources",
        lambda *args, **kwargs: (
            [
                RawArticle(
                    source_key="tqi_daily",
                    source_label="TQI Daily",
                    source_url="https://thequantuminsider.com/category/daily/",
                    section_key="tqi_daily",
                    title="Quantum Story",
                    canonical_url="https://thequantuminsider.com/story/",
                    published_at=now,
                )
            ],
            [
                SourceHealth(
                    source_key="tqi_daily",
                    requested=True,
                    success=True,
                    items_seen=1,
                    items_in_window=1,
                    fallback_mode_used="rss",
                )
            ],
        ),
    )

    run_weekly_quantum_pipeline(config, now=now)
    state = load_run_state(config.state_path)
    assert state.last_delivery_status == "dry_run"
    assert state.last_successful_window_end is None


def test_pipeline_writes_audio_outputs_when_tts_enabled(tmp_path: Path, monkeypatch):
    now = datetime(2026, 3, 16, 0, 0, tzinfo=UTC)
    config = make_config(
        output_dir=tmp_path / "output" / "weekly_quantum",
        state_path=tmp_path / "state" / "weekly_quantum_run_state.json",
        gemini_api_key="test-key",
        skip_llm=False,
        skip_tts=False,
        skip_telegram=True,
        dry_run=True,
    )

    monkeypatch.setattr(
        "morning_radio.weekly_quantum.pipeline._collect_sources",
        lambda *args, **kwargs: (
            [
                RawArticle(
                    source_key="tqi_business",
                    source_label="TQI Business",
                    source_url="https://thequantuminsider.com/category/daily/business/",
                    section_key="business",
                    title="Quantum startup lands new funding",
                    canonical_url="https://thequantuminsider.com/story/",
                    published_at=now,
                    excerpt="Funding round points to near-term commercialization.",
                )
            ],
            [
                SourceHealth(
                    source_key="tqi_business",
                    requested=True,
                    success=True,
                    items_seen=1,
                    items_in_window=1,
                    fallback_mode_used="rss",
                )
            ],
        ),
    )

    class FakeEditor:
        def __init__(self, config):
            self.config = config

        def create_category_brief(self, **kwargs):
            return CategoryBrief(
                category_key="industry_business",
                category_label="산업과 투자",
                lead_summary="이번 주는 사업화 흐름이 가장 강하게 보였습니다.",
                items=[
                    BriefItem(
                        headline="Quantum startup lands new funding",
                        summary="신규 자금 유입이 상용화 단계 진입 기대를 키웠습니다.",
                        why_it_matters="시장 내 자본 흐름과 실행 속도를 확인하게 합니다.",
                        sources=["TQI Business"],
                        cluster_id="global-001",
                        confidence="high",
                    )
                ],
            )

        def create_weekly_show(self, *, briefs, window):
            return WeeklyShow(
                window_start=window.start,
                window_end=window.end,
                host_name=self.config.host_name,
                analyst_name=self.config.analyst_name,
                show_title="주간 양자 브리핑",
                show_summary="산업 흐름 중심으로 정리한 테스트 주간본입니다.",
                opening=f"{self.config.host_name}: 테스트 오프닝입니다.",
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
                closing=f"{self.config.host_name}: 테스트 클로징입니다.",
                headline_script_text=f"{self.config.host_name}: 헤드라인 테스트입니다.",
                full_script_text=(
                    f"{self.config.host_name}: 테스트 오프닝입니다.\n\n"
                    f"{self.config.analyst_name}: 산업 흐름 중심으로 정리했습니다."
                ),
                full_script_markdown=(
                    f"{self.config.host_name}: 테스트 오프닝입니다.\n\n"
                    f"{self.config.analyst_name}: 산업 흐름 중심으로 정리했습니다."
                ),
            )

        def generate_audio(self, script_text):
            return b"fake-mp3", "audio/mpeg"

    monkeypatch.setattr("morning_radio.weekly_quantum.pipeline.WeeklyGeminiStudio", FakeEditor)

    run_dir = run_weekly_quantum_pipeline(config, now=now)

    assert (run_dir / "weekly_full.mp3").read_bytes() == b"fake-mp3"
    assert not (run_dir / "weekly_headlines.mp3").exists()
