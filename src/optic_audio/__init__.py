"""Optic Audio Engine: local-first acoustic measurements.

Public API:
    analyze_audio(path, sample_rate=None) -> AudioSummary
    AudioSummary.to_dict() -> dict
"""

from .analyzer import AudioSummary, analyze_audio

__all__ = ["AudioSummary", "analyze_audio"]

__version__ = "0.1.0"
