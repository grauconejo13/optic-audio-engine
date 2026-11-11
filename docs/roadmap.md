# Roadmap

This roadmap tracks planned milestones and completed engineering work.

## Milestone 0: Documentation and scope

- [x] Public repository established
- [x] Project README
- [x] Architecture outline
- [x] Development roadmap
- [ ] Select an open-source license

## Milestone 1: Minimal working Python package

- [x] Add `pyproject.toml` and `src/optic_audio` package
- [x] Implement WAV loading and validation
- [x] Calculate duration and RMS amplitude
- [x] Write pytest tests for synthetic signals
- [x] Add a CLI for local JSON analysis

## Milestone 2: Acoustic features

- [x] Pitch estimation on voiced segments
- [x] Configurable silence detection
- [x] Well-defined null/unknown pitch values and units
- [x] Tests for silence, tones, thresholds, and sample-rate differences
- [ ] Add explicit stereo-input coverage

## Milestone 3: Engineering quality

- [x] GitHub Actions CI for automated tests
- [ ] Type checking / linting
- [x] API and CLI documentation with usage examples
- [ ] Versioned releases and change log

## Milestone 4: Integration readiness

- [ ] Stable JSON-compatible output schema
- [ ] Performance benchmarks using non-personal test audio
- [ ] Optional integration with a separate Optic application or API

## Non-goals

The initial project does not claim to infer confidence, identity, mental state, or health from a voice recording.

## Suggested next commit

`chore: add linting and static type checks`
