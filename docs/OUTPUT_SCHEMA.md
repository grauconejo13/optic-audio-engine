# JSON output contract

This document defines the current JSON-compatible output contract produced by `AudioSummary.to_dict()` and the `optic-audio` CLI.

## Top-level object

The output is an object with exactly these fields:

| Field | Type | Units / meaning |
| --- | --- | --- |
| `duration_seconds` | number | Recording duration in seconds |
| `rms` | number | Root-mean-square amplitude on the normalized waveform sample scale |
| `sample_rate_hz` | integer | Samples per second after any requested resampling |
| `sample_count` | integer | Number of mono waveform samples analyzed |
| `fundamental_frequency_hz` | number or null | Median pYIN fundamental-frequency estimate across voiced frames |
| `silence_intervals` | array | Contiguous low-amplitude intervals that satisfy the configured threshold and minimum duration |

## Silence interval object

Each element of `silence_intervals` is an object with exactly these fields:

| Field | Type | Units / meaning |
| --- | --- | --- |
| `start_seconds` | number | Inclusive interval start time in seconds |
| `end_seconds` | number | Interval end time in seconds |
| `duration_seconds` | number | `end_seconds - start_seconds` |

## Null and empty behavior

- `fundamental_frequency_hz` is `null` when voiced pitch is not detected reliably enough to report.
- `silence_intervals` is an empty array when no interval meets the configured silence criteria.
- Numeric measurements are finite JSON numbers. NaN and Infinity are not part of the contract.

## Compatibility policy

Until the first tagged 1.0 release, the schema is still pre-1.0. Changes to field names, types, units, null behavior, or nested structure must:

1. be documented in `CHANGELOG.md`,
2. include regression-test updates,
3. be called out as an integration-facing change.

Additive fields may still affect strict consumers, so they should also be treated as schema changes.

## Scope

The schema reports measurable acoustic properties only. It does not encode confidence, emotion, credibility, identity, health, or other inferred personal traits.
