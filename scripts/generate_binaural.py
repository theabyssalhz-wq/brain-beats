#!/usr/bin/env python3
"""Generate binaural beat audio for Brain Beats — pure tones, no voice.

Brain Beats is voice-free. The binaural is the centrepiece, not background.
We generate stereo left/right carrier tones with the beat frequency as the
difference, then apply a gentle fade-in/out envelope.

Usage: python scripts/generate_binaural.py 01
"""

import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Carrier base — we keep it low/mid so it doesn't fatigue after long sessions
DEFAULT_CARRIER_HZ = 200.0
# For carrier-range frequencies (> 50Hz) we still embed them as-is
CARRIER_THRESHOLD = 50.0

FADE_SEC  = 10    # fade in + fade out duration
VOLUME_DB = -6    # master level — headroom for mixing with ambient


def _derive_channels(freq_str: str) -> tuple[float, float]:
    hz = float(re.sub(r"[^\d.]", "", freq_str))
    if hz <= CARRIER_THRESHOLD:
        # Subcarrier mode: left=200Hz, right=200+beat
        return DEFAULT_CARRIER_HZ, DEFAULT_CARRIER_HZ + hz
    else:
        # Direct mode: left=freq, right=freq+4Hz (universal beat)
        return hz, hz + 4.0


def run(row_id: str) -> None:
    csv_path = ROOT / "content_plan.csv"
    with open(csv_path, newline="", encoding="utf-8") as f:
        row = next((r for r in csv.DictReader(f) if r["id"] == row_id), None)
    if row is None:
        print(f"ERROR: row {row_id!r} not found", file=sys.stderr); sys.exit(1)

    freq    = row["frequency"]
    dur_h   = int(row.get("duration_hours", 3))
    dur_s   = dur_h * 3600
    left_hz, right_hz = _derive_channels(freq)
    beat_hz = right_hz - left_hz

    out_dir = ROOT / "output" / "binaural"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{row_id}_{freq}_{dur_h}h.mp3"

    print(f"Brain Beats {row_id} | {freq}")
    print(f"  Left:  {left_hz:.2f}Hz  |  Right: {right_hz:.2f}Hz  |  Beat: {beat_hz:.2f}Hz")
    print(f"  Duration: {dur_h}h ({dur_s}s)")
    print(f"  Output: {out_path}")
    print("Generating...")

    af = (
        f"[0:a]volume={VOLUME_DB}dB,"
        f"afade=t=in:st=0:d={FADE_SEC},"
        f"afade=t=out:st={dur_s - FADE_SEC}:d={FADE_SEC}[left];"
        f"[1:a]volume={VOLUME_DB}dB,"
        f"afade=t=in:st=0:d={FADE_SEC},"
        f"afade=t=out:st={dur_s - FADE_SEC}:d={FADE_SEC}[right];"
        f"[left][right]amerge=inputs=2,pan=stereo|c0<c0|c1<c1[a]"
    )

    cmd = [
        "ffmpeg",
        "-f", "lavfi", "-i", f"sine=frequency={left_hz}:duration={dur_s}",
        "-f", "lavfi", "-i", f"sine=frequency={right_hz}:duration={dur_s}",
        "-filter_complex", af,
        "-map", "[a]",
        "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100",
        str(out_path), "-y"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg error:\n{result.stderr[-800:]}", file=sys.stderr); sys.exit(1)

    size_mb = out_path.stat().st_size / 1_048_576
    print(f"Done. {size_mb:.1f} MB")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <row_id>"); sys.exit(1)
    run(sys.argv[1])
