"""Core audio loading and basic waveform measurements for Optic.

This module intentionally reports physical/numerical features only. It does not
infer a speaker's identity, emotion, health, or credibility.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import librosa
import numpy as np


@dataclass(frozen=True)
class AudioSummary:
    """Basic audio measurements with normalized floating-point waveform units."""

    duration_seconds: float
    rms: float
    sample_rate_hz: int
    sample_count: int

    def to_dict(self) -> dict[str, float | int]:
        """Return a JSON-serializable dictionary of numeric measurements."""
        return asdict(self)


def analyze_audio(
    path: str | Path,
    *,
    sample_rate: int | None = None,
) -> AudioSummary:
    """Load an audio file and compute its duration and RMS amplitude.

    Args:
        path: Local audio file path (WAV recommended for the initial milestone).
        sample_rate: Optional target sample rate. None preserves source rate.

    Raises:
        ValueError: If the sample rate is invalid or the recording is empty.
        FileNotFoundError: If the requested path does not exist.
        librosa/audioread exceptions: If decoding fails.

    Notes:
        Audio is converted to mono by librosa. RMS is relative to the waveform
        sample scale, **not** calibrated sound-pressure level (dB SPL).
    """
    if sample_rate is not None and (
        isinstance(sample_rate, bool)
        or not isinstance(sample_rate, int)
        or sample_rate <= 0
    ):
        raise ValueError("sample_rate must be a positive integer or None")

    audio_path = Path(path)
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    samples, sr = librosa.load(
        str(audio_path), sr=sample_rate, mono=True
    )
    if sr <= 0 or samples.size == 0:
        raise ValueError("Audio recording must contain at least one sample")
    if not np.all(np.isfinite(samples)):
        raise ValueError("Audio recording contains non-finite samples")

    # Use float64 for accumulation to reduce precision loss on long recordings.
    waveform = np.asarray(samples, dtype=np.float64)
    rms = float(np.sqrt(np.mean(np.square(waveform))))
    return AudioSummary(
        duration_seconds=float(waveform.size / sr),
        rms=rms,
        sample_rate_hz=int(sr),
        sample_count=int(waveform.size),
    )
