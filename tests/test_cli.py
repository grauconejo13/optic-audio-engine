"""CLI smoke tests for Optic Audio Engine."""

import json
import wave

import numpy as np

from optic_audio.cli import main


def write_pcm16_wav(path, samples, sample_rate=8000):
    samples = np.asarray(samples, dtype=np.float64)
    pcm = np.round(np.clip(samples, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(sample_rate)
        stream.writeframes(pcm.tobytes())


def test_cli_prints_json_summary(tmp_path, capsys):
    path = tmp_path / "silence.wav"
    write_pcm16_wav(path, np.zeros(8000))

    exit_code = main([str(path), "--indent", "0"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["duration_seconds"] == 1.0
    assert payload["sample_rate_hz"] == 8000
    assert payload["fundamental_frequency_hz"] is None
    assert payload["silence_intervals"][0]["duration_seconds"] == 1.0


def test_cli_passes_analysis_options(tmp_path, capsys):
    path = tmp_path / "quiet.wav"
    write_pcm16_wav(path, np.full(8000, 0.02))

    main(
        [
            str(path),
            "--silence-threshold",
            "0.03",
            "--min-silence-duration",
            "0.5",
            "--sample-rate",
            "4000",
            "--indent",
            "0",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["sample_rate_hz"] == 4000
    assert len(payload["silence_intervals"]) == 1
