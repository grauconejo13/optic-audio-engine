# Optic Audio Engine

A modular, open-source Python toolkit for extracting measurable acoustic features from audio recordings.

> **Status:** Early implementation. The core package can load local audio, preserve or resample sample rate, and report duration, RMS amplitude, sample rate, and sample count. Automated tests run across Python 3.10–3.12.

## Purpose

Optic Audio Engine is an independent audio-analysis component designed to support research, experimentation, and future integrations with speech-feedback applications. Its goal is to produce **explainable, reproducible measurements**, not to judge a person's confidence, personality, or identity.

## Implemented

- Load local audio files with librosa
- Convert input to mono for consistent analysis
- Preserve the source sample rate or resample to a requested rate
- Measure duration in seconds
- Measure root-mean-square (RMS) waveform amplitude
- Report sample rate and sample count
- Return measurements through a typed `AudioSummary` object
- Convert results to a JSON-serializable dictionary
- Reject missing files, invalid sample rates, empty recordings, and non-finite samples
- Test duration, RMS, resampling, and invalid input behavior with pytest
- Run the test suite in CI on Python 3.10, 3.11, and 3.12

## Next features

- Estimate fundamental frequency (pitch) where detectable
- Identify silent intervals using configurable thresholds
- Expand machine-readable feature output
- Add reusable synthetic audio fixtures and examples
- Document measurement assumptions for each additional acoustic feature

## Technology

- **Python** for package architecture and processing
- **NumPy** for numerical operations
- **librosa** for audio loading and signal processing
- **pytest** for repeatable tests
- **GitHub Actions** for the Python compatibility test matrix

## Package layout

```text
optic-audio-engine/
├── src/optic_audio/
│   ├── __init__.py
│   └── analyzer.py
├── tests/
│   └── test_analyzer.py
├── docs/
│   ├── architecture.md
│   └── roadmap.md
├── .github/workflows/
│   └── tests.yml
├── pyproject.toml
└── README.md
```

## Current API

```python
from optic_audio import analyze_audio

summary = analyze_audio("recording.wav")

print(summary.duration_seconds)
print(summary.rms)
print(summary.sample_rate_hz)
print(summary.sample_count)
print(summary.to_dict())
```

An optional target sample rate can be supplied:

```python
summary = analyze_audio("recording.wav", sample_rate=16_000)
```

## Example output

```json
{
  "duration_seconds": 8.4,
  "rms": 0.12,
  "sample_rate_hz": 44100,
  "sample_count": 370440
}
```

RMS is relative to the normalized waveform sample scale. It is **not** a calibrated sound-pressure measurement such as dB SPL.

## Development

Install the package with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

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
