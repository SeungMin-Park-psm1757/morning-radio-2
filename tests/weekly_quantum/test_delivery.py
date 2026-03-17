from pathlib import Path

from morning_radio.weekly_quantum.delivery import public_links_for_run

from .conftest import make_config


def test_public_links_for_run_includes_audio_when_present(tmp_path: Path):
    run_dir = tmp_path / "20260317-063000"
    run_dir.mkdir()
    full_audio = run_dir / "weekly_full.mp3"
    full_audio.write_bytes(b"mp3")

    config = make_config(public_archive_base_url="https://example.com/weekly")
    links = public_links_for_run(
        config=config,
        run_dir=run_dir,
        full_audio_path=full_audio,
        headlines_audio_path=None,
    )

    assert links == {
        "summary": "https://example.com/weekly/20260317-063000/summary.md",
        "digest": "https://example.com/weekly/20260317-063000/message_digest.md",
        "full_audio": "https://example.com/weekly/20260317-063000/weekly_full.mp3",
    }
