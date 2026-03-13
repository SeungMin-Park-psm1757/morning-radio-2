import pytest

from morning_radio.weekly_quantum.collectors.base import SourceConfig
from morning_radio.weekly_quantum.config import build_source_configs, validate_source_configs


def test_build_source_configs_matches_approved_source_count():
    configs = build_source_configs(80)
    assert len(configs) == 12
    assert all(config.max_items_per_run == 80 for config in configs)


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
