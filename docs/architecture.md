# Architecture

## Design goals

1. **Separate concerns:** audio loading, feature extraction, aggregation, and output formatting should be independent.
2. **Reproducibility:** the same input and configuration should produce consistent measurements.
3. **Transparency:** document units, thresholds, assumptions, and uncertainty.
4. **Privacy:** perform core analysis locally; do not require an external service.
5. **Testability:** use generated audio fixtures to test edge cases without distributing personal recordings.

## Planned data flow

```text
Local WAV file
  -> input validation / decoding
  -> waveform + sample-rate normalization
  -> acoustic feature extraction
  -> metric aggregation
  -> structured result (Python object / JSON-compatible dictionary)
```

## Proposed components

| Module | Responsibility |
| --- | --- |
| `analyzer.py` | Orchestrate validation and feature extraction |
| `features.py` | Implement duration, RMS, pitch, and silence metrics |
| `tests/` | Test numerical behavior and edge cases |
| `examples/` | Demonstrate local invocation |

Exact public interfaces and package structure will be finalized during implementation.

## Measurement guidance

- **Duration:** seconds, derived from samples and sample rate.
- **RMS:** amplitude relative to the decoded waveform scale; not calibrated sound pressure level (dB SPL).
- **Pitch:** estimate fundamental frequency on sufficiently voiced intervals, with unavailable values represented explicitly.
- **Silence ratio:** fraction of recording classified as silent under a documented, configurable threshold.

## Edge cases to test

- Empty and extremely short recordings
- Silence-only audio
- Pure tones with known frequencies
- Stereo versus mono input
- Inconsistent sample rates
- Corrupted or unsupported files
- Background noise and low-volume speech

## Out of scope for the initial engine

- Speech recognition or transcript generation
- Speaker identification
- Emotion, deception, or personality inference
- Clinical voice diagnosis
- Real-time audio streaming

A future frontend or API may consume the engine's output without introducing a dependency in the core library.
