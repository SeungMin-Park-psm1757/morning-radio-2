import pytest

from morning_radio.weekly_quantum.collectors.base import SourceConfig
from morning_radio.weekly_quantum.config import build_parser, build_source_configs, load_weekly_quantum_config, validate_source_configs


def test_build_source_configs_matches_approved_source_count():
    configs = build_source_configs(80)
    assert len(configs) == 13
    assert all(0 < config.max_items_per_run <= 80 for config in configs)
    assert min(config.max_items_per_run for config in configs) == 8
    assert max(config.max_items_per_run for config in configs) == 40


def test_validate_source_configs_rejects_duplicate_keys():
    configs = [
        SourceConfig(
            key="dup",
            label="One",
            start_urls=["https://example.com/one"],
            collection_mode="direct",
            kind="tqi",
            max_items_per_run=10,
        ),
        SourceConfig(
            key="dup",
            label="Two",
            start_urls=["https://example.com/two"],
            collection_mode="direct",
            kind="qcr",
            max_items_per_run=10,
        ),
    ]
    with pytest.raises(ValueError, match="Duplicate source key"):
        validate_source_configs(configs)


def test_load_config_keeps_fixed_speaker_labels(monkeypatch):
    monkeypatch.setenv("WEEKLY_QUANTUM_HOST_NAME", "민준")
    monkeypatch.setenv("WEEKLY_QUANTUM_ANALYST_NAME", "서연")
    monkeypatch.setenv("WEEKLY_QUANTUM_TTS_SPEED", "0.94")
    config = load_weekly_quantum_config(build_parser().parse_args([]))
    assert config.host_name == "진행자"
    assert config.analyst_name == "해설"
    assert config.tts_speed_multiplier == 0.94
