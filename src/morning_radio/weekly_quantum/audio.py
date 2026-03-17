from __future__ import annotations

import array
import re
from pathlib import Path


def write_audio_output(
    *,
    run_dir: Path,
    audio_bytes: bytes,
    mime_type: str,
    file_name: str,
    bitrate_kbps: int,
) -> Path:
    lowered = mime_type.lower()
    output_path = run_dir / file_name
    if "audio/l16" in lowered or "codec=pcm" in lowered:
        sample_rate = _parse_sample_rate(lowered)
        pcm_bytes = _select_pcm_stream(audio_bytes)
        output_path.write_bytes(_encode_mp3(pcm_bytes, sample_rate, bitrate_kbps))
        return output_path

    output_path.write_bytes(audio_bytes)
    return output_path


def _parse_sample_rate(mime_type: str) -> int:
    match = re.search(r"rate=(\d+)", mime_type)
    if match:
        return int(match.group(1))
    return 24000


def _select_pcm_stream(audio_bytes: bytes) -> bytes:
    trimmed = audio_bytes[: len(audio_bytes) - (len(audio_bytes) % 2)]
    if not trimmed:
        raise ValueError("Gemini TTS returned an empty PCM payload.")

    swapped = b"".join(
        trimmed[index + 1 : index + 2] + trimmed[index : index + 1]
        for index in range(0, len(trimmed), 2)
    )
    return trimmed if _pcm_score(trimmed) <= _pcm_score(swapped) else swapped


def _pcm_score(pcm_bytes: bytes) -> float:
    probe = pcm_bytes[: min(len(pcm_bytes), 24000 * 2 * 12)]
    samples = array.array("h")
    samples.frombytes(probe)
    if not samples:
        return float("inf")

    if len(samples) > 12000:
        samples = samples[::4]

    mean_abs = sum(abs(sample) for sample in samples) / len(samples)
    delta = sum(abs(samples[index] - samples[index - 1]) for index in range(1, len(samples))) / max(len(samples) - 1, 1)
    clip_ratio = sum(1 for sample in samples if abs(sample) >= 30000) / len(samples)
    return (delta / max(mean_abs, 1.0)) + (clip_ratio * 3.0)


def _encode_mp3(pcm_bytes: bytes, sample_rate: int, bitrate_kbps: int) -> bytes:
    import lameenc

    encoder = lameenc.Encoder()
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)
    encoder.set_bit_rate(bitrate_kbps)
    encoder.set_quality(5)
    return encoder.encode(pcm_bytes) + encoder.flush()
