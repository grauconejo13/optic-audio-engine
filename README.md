# Optic Audio Engine

A modular, open-source Python toolkit for extracting measurable acoustic features from audio recordings.

> **Status:** Early implementation. The package reports duration, RMS amplitude, sample rate, sample count, fundamental frequency where detectable, and configurable silent intervals. It can be used from Python or from the `optic-audio` command line.

## Purpose

Optic Audio Engine is an independent audio-analysis component designed to support research, experimentation, and future integrations with speech-feedback applications. Its goal is to produce **explainable, reproducible measurements**, not to judge a person's confidence, personality, or identity.

## Implemented

- Load local audio files with librosa
- Convert input to mono for consistent analysis
- Preserve the source sample rate or resample to a requested rate
- Measure duration in seconds and waveform RMS
- Estimate median fundamental frequency with pYIN for voiced frames
- Detect configurable contiguous silent intervals
- Return typed Python measurement objects and JSON-serializable output
- Analyze files from a local CLI
- Test tones, silence, thresholds, resampling, invalid inputs, and CLI behavior
- Run the test suite in CI on Python 3.10, 3.11, and 3.12

## Python API

```python
from optic_audio import analyze_audio

summary = analyze_audio(
    "recording.wav",
    silence_threshold=0.01,
    min_silence_duration=0.2,
)

print(summary.fundamental_frequency_hz)
print(summary.silence_intervals)
print(summary.to_dict())
```

## Command line

Install the project with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Then analyze a local file:

```bash
optic-audio recording.wav
```

Example with options:

```bash
optic-audio recording.wav \
  --sample-rate 16000 \
  --silence-threshold 0.015 \
  --min-silence-duration 0.3
```

The command prints the same JSON-compatible measurement schema exposed by `AudioSummary.to_dict()`. Use `--indent 0` for compact JSON.

## Example output

```json
{
  "duration_seconds": 8.4,
  "rms": 0.12,
  "sample_rate_hz": 44100,
  "sample_count": 370440,
  "fundamental_frequency_hz": 184.7,
  "silence_intervals": [
    {
      "start_seconds": 2.1,
      "end_seconds": 2.8,
      "duration_seconds": 0.7
    }
  ]
}
```

RMS and silence thresholds use the normalized waveform sample scale. They are **not** calibrated sound-pressure measurements such as dB SPL.

Fundamental frequency is estimated with librosa's pYIN implementation across voiced frames, then summarized with the median. The current search range is C2-C7 (approximately 65-2093 Hz). A value of `null` / `None` means the analyzer did not detect voiced pitch reliably enough to report a value.

Silence detection groups samples at or below the configured absolute-amplitude threshold into contiguous intervals and discards intervals shorter than `min_silence_duration`. These intervals represent low waveform amplitude, not semantic pauses or speech boundaries.

## Development

Run the tests:

```bash
pytest
```

## Documentation

- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)

## Privacy and scope

Local-first processing is the default. The current engine reads local files and does not require recording uploads or cloud APIs. Voice measurements alone cannot reliably infer emotions, credibility, personality, identity, or medical conditions.

## Contributing

Feature suggestions, reproducible bug reports, and focused tests are welcome. New measurements should include documented units, assumptions, failure behavior, and repeatable tests.

## License

License choice is pending. Until a license is added, public availability does **not** grant blanket permission to copy, modify, or redistribute this code.
