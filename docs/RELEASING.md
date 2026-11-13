# Release process

Optic Audio Engine uses Semantic Versioning: `MAJOR.MINOR.PATCH`.

## Pre-1.0 policy

While the project is below 1.0:

- PATCH releases are for fixes, documentation corrections, and internal quality work that do not intentionally change the public schema.
- MINOR releases may add measurements, CLI options, or make documented API/schema changes.
- Breaking changes must be called out clearly in `CHANGELOG.md`.

## Release checklist

1. Run the local quality gate:

   ```bash
   ruff check src tests
   mypy src
   pytest
   ```

2. Confirm CI passes on Python 3.10, 3.11, and 3.12.
3. Update `CHANGELOG.md`, moving relevant entries out of **Unreleased**.
4. Update the version in `pyproject.toml`.
5. Verify README examples against the release candidate.
6. Create an annotated Git tag in the form `vX.Y.Z`.
7. Create GitHub release notes from the changelog entry.

## Current state

The package declares version `0.1.0`, but no tagged public release is implied by the version alone. The first tagged release should happen only after the JSON-compatible output schema is reviewed for integration stability.
