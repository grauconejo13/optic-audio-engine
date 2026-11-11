"""Optic Audio Engine: local-first acoustic measurements.

Public API:
    analyze_audio(...) -> AudioSummary
    AudioSummary.to_dict() -> dict
"""

from .analyzer import AudioSummary, SilenceInterval, analyze_audio

__all__ = ["AudioSummary", "SilenceInterval", "analyze_audio"]

__version__ = "0.1.0"
