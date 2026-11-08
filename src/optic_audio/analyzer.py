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
class AudioSummary:
    """Audio measurements with normalized floating-point waveform units."""

    duration_seconds: float
    rms: float
    sample_rate_hz: int
    sample_count: int
    fundamental_frequency_hz: float | None

    def to_dict(self) -> dict[str, float | int | None]:
        """Return a JSON-serializable dictionary of numeric measurements."""
        return asdict(self)


def _estimate_fundamental_frequency(
    waveform: np.ndarray,
    sample_rate_hz: int,
) -> float | None:
    """Estimate median fundamental frequency for voiced frames.

    librosa.pyin returns frame-level estimates plus a voiced/unvoiced mask.
    A median is used so a few unstable frames do not dominate the summary.
    """
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


def analyze_audio(
    path: str | Path,
    *,
    sample_rate: int | None = None,
) -> AudioSummary:
    """Load an audio file and compute basic acoustic measurements.

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

        Fundamental frequency is a median pYIN estimate across frames that
        librosa identifies as voiced. It is None when no reliable voiced frames
        are detected. The estimate is limited to C2-C7 (about 65-2093 Hz).
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
    fundamental_frequency_hz = _estimate_fundamental_frequency(waveform, int(sr))

    return AudioSummary(
        duration_seconds=float(waveform.size / sr),
        rms=rms,
        sample_rate_hz=int(sr),
        sample_count=int(waveform.size),
        fundamental_frequency_hz=fundamental_frequency_hz,
    )
