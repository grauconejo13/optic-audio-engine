"""Regression tests for the basic Optic audio analyzer.

Run after installing the package with: pip install -e ".[dev]"
Then: pytest
"""

import math
import wave

import numpy as np
import pytest

from optic_audio import AudioSummary, analyze_audio


def write_pcm16_wav(path, samples, sample_rate=16000):
    """Write deterministic mono 16-bit PCM without external test fixtures."""
    samples = np.asarray(samples, dtype=np.float64)
    pcm = np.round(np.clip(samples, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(sample_rate)
        stream.writeframes(pcm.tobytes())


def test_sine_wave_duration_and_rms(tmp_path):
    sr = 16000
    t = np.arange(sr, dtype=np.float64) / sr
    samples = 0.5 * np.sin(2 * np.pi * 440 * t)
    path = tmp_path / "tone.wav"
    write_pcm16_wav(path, samples, sr)

    result = analyze_audio(path)
    assert isinstance(result, AudioSummary)
    assert result.duration_seconds == pytest.approx(1.0)
    assert result.sample_count == sr
    assert result.sample_rate_hz == sr
    assert result.rms == pytest.approx(0.5 / math.sqrt(2), abs=1e-3)
    assert result.to_dict()["rms"] == result.rms


def test_silence_has_zero_rms(tmp_path):
    path = tmp_path / "silence.wav"
    write_pcm16_wav(path, np.zeros(8000), sample_rate=8000)
    result = analyze_audio(path)
    assert result.duration_seconds == pytest.approx(1.0)
    assert result.rms == pytest.approx(0.0)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        analyze_audio(tmp_path / "missing.wav")


@pytest.mark.parametrize("sample_rate", [0, -1, True, 16000.5])
def test_invalid_target_sample_rate_raises(tmp_path, sample_rate):
    path = tmp_path / "sample.wav"
    write_pcm16_wav(path, np.zeros(100))
    with pytest.raises(ValueError, match="sample_rate"):
        analyze_audio(path, sample_rate=sample_rate)


def test_resampling_changes_sample_count_not_duration(tmp_path):
    path = tmp_path / "sample.wav"
    write_pcm16_wav(path, np.zeros(16000), sample_rate=16000)
    result = analyze_audio(path, sample_rate=8000)
    assert result.sample_rate_hz == 8000
    assert result.sample_count == 8000
    assert result.duration_seconds == pytest.approx(1.0)
