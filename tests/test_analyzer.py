"""Regression tests for the Optic audio analyzer."""

import math
import wave

import numpy as np
import pytest

from optic_audio import AudioSummary, SilenceInterval, analyze_audio


def write_pcm16_wav(path, samples, sample_rate=16000):
    """Write deterministic mono 16-bit PCM without external test fixtures."""
    samples = np.asarray(samples, dtype=np.float64)
    pcm = np.round(np.clip(samples, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(sample_rate)
        stream.writeframes(pcm.tobytes())


def write_stereo_pcm16_wav(path, left, right, sample_rate=16000):
    """Write deterministic stereo 16-bit PCM with interleaved channels."""
    left = np.asarray(left, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    if left.shape != right.shape:
        raise ValueError("Stereo channels must have the same shape")

    stereo = np.column_stack([left, right])
    pcm = np.round(np.clip(stereo, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(2)
        stream.setsampwidth(2)
        stream.setframerate(sample_rate)
        stream.writeframes(pcm.tobytes())


def test_sine_wave_duration_rms_and_pitch(tmp_path):
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
    assert result.fundamental_frequency_hz == pytest.approx(440.0, abs=3.0)
    assert result.silence_intervals == ()
    assert result.to_dict()["rms"] == result.rms


def test_second_tone_tracks_different_fundamental_frequency(tmp_path):
    sr = 22050
    t = np.arange(sr, dtype=np.float64) / sr
    samples = 0.4 * np.sin(2 * np.pi * 220 * t)
    path = tmp_path / "a3.wav"
    write_pcm16_wav(path, samples, sr)

    result = analyze_audio(path)

    assert result.fundamental_frequency_hz == pytest.approx(220.0, abs=3.0)


def test_silence_has_zero_rms_no_pitch_and_full_interval(tmp_path):
    path = tmp_path / "silence.wav"
    write_pcm16_wav(path, np.zeros(8000), sample_rate=8000)

    result = analyze_audio(path)

    assert result.duration_seconds == pytest.approx(1.0)
    assert result.rms == pytest.approx(0.0)
    assert result.fundamental_frequency_hz is None
    assert result.silence_intervals == (
        SilenceInterval(0.0, 1.0, 1.0),
    )


def test_detects_silence_between_two_tones(tmp_path):
    sr = 8000
    tone_t = np.arange(sr // 2, dtype=np.float64) / sr
    tone = 0.4 * np.sin(2 * np.pi * 220 * tone_t)
    samples = np.concatenate([tone, np.zeros(sr // 2), tone])
    path = tmp_path / "tone-silence-tone.wav"
    write_pcm16_wav(path, samples, sr)

    result = analyze_audio(path, silence_threshold=0.01, min_silence_duration=0.25)

    assert len(result.silence_intervals) == 1
    interval = result.silence_intervals[0]
    assert interval.start_seconds == pytest.approx(0.5, abs=0.002)
    assert interval.end_seconds == pytest.approx(1.0, abs=0.002)
    assert interval.duration_seconds == pytest.approx(0.5, abs=0.002)


def test_silence_threshold_is_configurable(tmp_path):
    sr = 8000
    samples = np.full(sr, 0.02)
    path = tmp_path / "quiet.wav"
    write_pcm16_wav(path, samples, sr)

    strict = analyze_audio(path, silence_threshold=0.01)
    permissive = analyze_audio(path, silence_threshold=0.03)

    assert strict.silence_intervals == ()
    assert len(permissive.silence_intervals) == 1
    assert permissive.silence_intervals[0].duration_seconds == pytest.approx(1.0)


def test_short_quiet_gap_is_ignored(tmp_path):
    sr = 8000
    tone_t = np.arange(sr // 2, dtype=np.float64) / sr
    tone = 0.4 * np.sin(2 * np.pi * 220 * tone_t)
    samples = np.concatenate([tone, np.zeros(int(sr * 0.05)), tone])
    path = tmp_path / "short-gap.wav"
    write_pcm16_wav(path, samples, sr)

    result = analyze_audio(path, min_silence_duration=0.2)

    assert result.silence_intervals == ()


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        analyze_audio(tmp_path / "missing.wav")


@pytest.mark.parametrize("sample_rate", [0, -1, True, 16000.5])
def test_invalid_target_sample_rate_raises(tmp_path, sample_rate):
    path = tmp_path / "sample.wav"
    write_pcm16_wav(path, np.zeros(100))
    with pytest.raises(ValueError, match="sample_rate"):
        analyze_audio(path, sample_rate=sample_rate)


@pytest.mark.parametrize("threshold", [-0.1, float("nan"), True])
def test_invalid_silence_threshold_raises(tmp_path, threshold):
    path = tmp_path / "sample.wav"
    write_pcm16_wav(path, np.zeros(100))
    with pytest.raises(ValueError, match="silence_threshold"):
        analyze_audio(path, silence_threshold=threshold)


@pytest.mark.parametrize("duration", [0, -0.1, float("nan"), True])
def test_invalid_minimum_silence_duration_raises(tmp_path, duration):
    path = tmp_path / "sample.wav"
    write_pcm16_wav(path, np.zeros(100))
    with pytest.raises(ValueError, match="min_silence_duration"):
        analyze_audio(path, min_silence_duration=duration)


def test_stereo_input_is_downmixed_to_mono_consistently(tmp_path):
    sr = 16000
    t = np.arange(sr, dtype=np.float64) / sr
    left = 0.5 * np.sin(2 * np.pi * 440 * t)
    right = np.zeros_like(left)
    path = tmp_path / "stereo-tone.wav"
    write_stereo_pcm16_wav(path, left, right, sr)

    result = analyze_audio(path)

    assert result.sample_rate_hz == sr
    assert result.sample_count == sr
    assert result.duration_seconds == pytest.approx(1.0)
    assert result.rms == pytest.approx(0.25 / math.sqrt(2), abs=1e-3)
    assert result.fundamental_frequency_hz == pytest.approx(440.0, abs=3.0)
    assert result.silence_intervals == ()


def test_resampling_changes_sample_count_not_duration(tmp_path):
    path = tmp_path / "sample.wav"
    write_pcm16_wav(path, np.zeros(16000), sample_rate=16000)
    result = analyze_audio(path, sample_rate=8000)
    assert result.sample_rate_hz == 8000
    assert result.sample_count == 8000
    assert result.duration_seconds == pytest.approx(1.0)
    assert result.fundamental_frequency_hz is None
