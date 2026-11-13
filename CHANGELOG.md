# Changelog

All notable changes to Optic Audio Engine will be documented here.

This project follows Semantic Versioning for release numbers once tagged releases begin.

## Unreleased

### Added

- Local audio analysis with duration, RMS, sample rate, and sample count
- Median fundamental-frequency estimation with pYIN
- Configurable silence interval detection
- Stereo-input downmix regression coverage
- JSON-serializable typed result objects
- `optic-audio` command-line interface
- pytest, Ruff, and mypy quality gates in GitHub Actions

### Notes

- The package version remains `0.1.0` while the public API and JSON schema are still early.
- No compatibility guarantee is made for pre-1.0 releases.
