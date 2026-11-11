"""Command-line interface for Optic Audio Engine."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from .analyzer import analyze_audio


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="optic-audio",
        description="Analyze a local audio file and print JSON measurements.",
    )
    parser.add_argument("path", help="Path to the audio file to analyze.")
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=None,
        help="Optional target sample rate in Hz.",
    )
    parser.add_argument(
        "--silence-threshold",
        type=float,
        default=0.01,
        help="Normalized absolute-amplitude silence threshold (default: 0.01).",
    )
    parser.add_argument(
        "--min-silence-duration",
        type=float,
        default=0.2,
        help="Minimum silence duration in seconds (default: 0.2).",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2). Use 0 for compact output.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Analyze one file and print its JSON-compatible summary."""
    args = build_parser().parse_args(argv)

    summary = analyze_audio(
        args.path,
        sample_rate=args.sample_rate,
        silence_threshold=args.silence_threshold,
        min_silence_duration=args.min_silence_duration,
    )
    indent = None if args.indent == 0 else args.indent
    print(json.dumps(summary.to_dict(), indent=indent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
