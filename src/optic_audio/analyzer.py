"""Core audio loading and measurable waveform features for Optic.

This module intentionally reports physical/numerical features only. It does not
infer a speaker's identity, emotion, health, or credibility.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import librosa
import numpy as np


@dataclass(frozen=True)
class SilenceInterval:
    """A contiguous low-amplitude interval measured in seconds."""

    start_seconds: float
    end_seconds: float
    duration_seconds: float


@dataclass(frozen=True)
class AudioSummary:
    """Audio measurements with normalized floating-point waveform units."""

    duration_seconds: float
    rms: float
    sample_rate_hz: int
    sample_count: int
    fundamental_frequency_hz: float | None
    silence_intervals: tuple[SilenceInterval, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable dictionary of measurements."""
        return asdict(self)


def _estimate_fundamental_frequency(
    waveform: np.ndarray,
    sample_rate_hz: int,
) -> float | None:
    """Estimate median fundamental frequency for voiced frames."""
    if waveform.size < 2048 or np.max(np.abs(waveform)) <= 1e-6:
        return None

    f0, voiced_flag, _ = librosa.pyin(
        waveform,
        fmin=float(librosa.note_to_hz("C2")),
        fmax=float(librosa.note_to_hz("C7")),
        sr=sample_rate_hz,
    )

    if f0 is None or voiced_flag is None:
        return None

    voiced_f0 = np.asarray(f0, dtype=np.float64)[np.asarray(voiced_flag, dtype=bool)]
    voiced_f0 = voiced_f0[np.isfinite(voiced_f0)]
    if voiced_f0.size == 0:
        return None

    return float(np.median(voiced_f0))


def _detect_silence_intervals(
    waveform: np.ndarray,
    sample_rate_hz: int,
    *,
    threshold: float,
    min_duration_seconds: float,
) -> tuple[SilenceInterval, ...]:
    """Return contiguous intervals whose absolute amplitude stays below threshold."""
    silent = np.abs(waveform) <= threshold
    padded = np.concatenate(([False], silent, [False]))
    transitions = np.diff(padded.astype(np.int8))
    starts = np.flatnonzero(transitions == 1)
    ends = np.flatnonzero(transitions == -1)

    minimum_samples = max(1, int(np.ceil(min_duration_seconds * sample_rate_hz)))
    intervals: list[SilenceInterval] = []

    for start, end in zip(starts, ends):
        if end - start < minimum_samples:
            continue
        start_seconds = float(start / sample_rate_hz)
        end_seconds = float(end / sample_rate_hz)
        intervals.append(
            SilenceInterval(
                start_seconds=start_seconds,
                end_seconds=end_seconds,
                duration_seconds=end_seconds - start_seconds,
            )
        )

    return tuple(intervals)


def analyze_audio(
    path: str | Path,
    *,
    sample_rate: int | None = None,
    silence_threshold: float = 0.01,
    min_silence_duration: float = 0.2,
) -> AudioSummary:
    """Load an audio file and compute basic acoustic measurements.

    Args:
        path: Local audio file path (WAV recommended for the initial milestone).
        sample_rate: Optional target sample rate. None preserves source rate.
        silence_threshold: Absolute normalized amplitude at or below which a
            sample is considered silent.
        min_silence_duration: Minimum contiguous silence duration to report.

    Raises:
        ValueError: If analysis parameters are invalid or the recording is empty.
        FileNotFoundError: If the requested path does not exist.
        librosa/audioread exceptions: If decoding fails.

    Notes:
        Audio is converted to mono by librosa. RMS is relative to the waveform
        sample scale, **not** calibrated sound-pressure level (dB SPL).

        Fundamental frequency is a median pYIN estimate across voiced frames.
        The search range is C2-C7 (about 65-2093 Hz).

        Silence detection is amplitude-based. It does not classify pauses,
        speech boundaries, or semantic content.
    """
    if sample_rate is not None and (
        isinstance(sample_rate, bool)
        or not isinstance(sample_rate, int)
        or sample_rate <= 0
    ):
        raise ValueError("sample_rate must be a positive integer or None")
    if (
        isinstance(silence_threshold, bool)
        or not isinstance(silence_threshold, (int, float))
        or not np.isfinite(silence_threshold)
        or silence_threshold < 0
    ):
        raise ValueError("silence_threshold must be a finite non-negative number")
    if (
        isinstance(min_silence_duration, bool)
        or not isinstance(min_silence_duration, (int, float))
        or not np.isfinite(min_silence_duration)
        or min_silence_duration <= 0
    ):
        raise ValueError("min_silence_duration must be a finite positive number")

    audio_path = Path(path)
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    samples, sr = librosa.load(str(audio_path), sr=sample_rate, mono=True)
    if sr <= 0 or samples.size == 0:
        raise ValueError("Audio recording must contain at least one sample")
    if not np.all(np.isfinite(samples)):
        raise ValueError("Audio recording contains non-finite samples")

    waveform = np.asarray(samples, dtype=np.float64)
    rms = float(np.sqrt(np.mean(np.square(waveform))))
    fundamental_frequency_hz = _estimate_fundamental_frequency(waveform, int(sr))
    silence_intervals = _detect_silence_intervals(
        waveform,
        int(sr),
        threshold=float(silence_threshold),
        min_duration_seconds=float(min_silence_duration),
    )

    return AudioSummary(
        duration_seconds=float(waveform.size / sr),
        rms=rms,
        sample_rate_hz=int(sr),
        sample_count=int(waveform.size),
        fundamental_frequency_hz=fundamental_frequency_hz,
        silence_intervals=silence_intervals,
    )
