# Roadmap

This roadmap tracks planned milestones, not completed features.

## Milestone 0: Documentation and scope

- [x] Public repository established
- [x] Project README
- [x] Architecture outline
- [x] Development roadmap
- [ ] Select an open-source license

## Milestone 1: Minimal working Python package

- [ ] Add `pyproject.toml` and `src/optic_audio` package
- [ ] Implement WAV loading and validation
- [ ] Calculate duration and RMS amplitude
- [ ] Write pytest tests for synthetic signals
- [ ] Add a CLI or local example script

**Acceptance criteria:** package can be installed locally; tests pass; a WAV file produces duration and RMS results.

## Milestone 2: Acoustic features

- [ ] Pitch estimation on voiced segments
- [ ] Configurable silence detection
- [ ] Well-defined null/unknown values and units
- [ ] Tests for silence, tones, stereo, and sample-rate differences

**Acceptance criteria:** documented outputs and tests cover expected numerical behavior and failure cases.

## Milestone 3: Engineering quality

- [ ] GitHub Actions CI for automated tests
- [ ] Type checking / linting
- [ ] API documentation and usage examples
- [ ] Versioned releases and change log

## Milestone 4: Integration readiness

- [ ] Stable JSON-compatible output schema
- [ ] Performance benchmarks using non-personal test audio
- [ ] Optional integration with a separate Optic application or API

## Non-goals

The initial project does not claim to infer confidence, identity, mental state, or health from a voice recording.

## Suggested next commit

`feat: bootstrap Python package with WAV analysis and pytest`
