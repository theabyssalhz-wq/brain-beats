#!/usr/bin/env python3
"""Generate ambient music bed for Brain Beats.

No voice. Ambient is the emotional canvas — binaural sits on top.
We loop a source ambient file from assets/ambient/ to the full video duration.

Usage: python scripts/generate_ambient.py 01
"""

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Map benefit keywords → ambient file
# Map benefit → visual file in assets/visuals/
VISUAL_MAP = {
    "sleep":      "dark_nebula.png",
    "delta":      "dark_nebula.png",
    "focus":      "particles_cyan.png",
    "study":      "particles_cyan.png",
    "gamma":      "particles_cyan.png",
    "adhd":       "particles_cyan.png",
    "healing":    "deep_cosmos.png",
    "chakra":     "deep_cosmos.png",
    "heart":      "deep_cosmos.png",
    "pineal":     "golden_cosmos.png",
    "grounding":  "earth_pulse.png",
    "earth":      "earth_pulse.png",
    "schumann":   "earth_pulse.png",
    "theta":      "void_ripple.png",
    "meditation": "void_ripple.png",
    "alpha":      "soft_void.png",
    "calm":       "soft_void.png",
    "anxiety":    "soft_void.png",
    "morning":    "dawn_light.png",
}
DEFAULT_VISUAL = "deep_cosmos.png"

# Ambient sits -18dB under binaural
AMBIENT_DB = -18


def _pick_ambient(benefit: str) -> str:
    b = benefit.lower()
    for keyword, fname in AMBIENT_MAP.items():
        if keyword in b:
            return fname
    return DEFAULT_AMBIENT


def run(row_id: str) -> None:
    csv_path = ROOT / "content_plan.csv"
    with open(csv_path, newline="", encoding="utf-8") as f:
        row = next((r for r in csv.DictReader(f) if r["id"] == row_id), None)
    if row is None:
        print(f"ERROR: row {row_id!r} not found", file=sys.stderr); sys.exit(1)

    freq    = row["frequency"]
    benefit = row["benefit"]
    dur_h   = int(row.get("duration_hours", 3))
    dur_s   = dur_h * 3600

    src_name = _pick_ambient(benefit)
    src = ROOT / "assets" / "ambient" / src_name
    if not src.exists():
        src = ROOT / "assets" / "ambient" / DEFAULT_AMBIENT
        src_name = DEFAULT_AMBIENT

    out_dir = ROOT / "output" / "ambient"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{row_id}_{freq}_{dur_h}h_ambient.mp3"

    print(f"Brain Beats {row_id} | {freq}")
    print(f"  Ambient: {src_name}  |  Duration: {dur_h}h")

    result = subprocess.run([
        "ffmpeg",
        "-stream_loop", "-1", "-i", str(src),
        "-t", str(dur_s),
        "-af", f"volume={AMBIENT_DB}dB,afade=t=in:st=0:d=10,afade=t=out:st={dur_s-10}:d=10",
        "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100",
        str(out_path), "-y"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"FFmpeg error:\n{result.stderr[-400:]}", file=sys.stderr); sys.exit(1)

    size_mb = out_path.stat().st_size / 1_048_576
    print(f"Done. {size_mb:.1f} MB  →  {out_path.name}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <row_id>"); sys.exit(1)
    run(sys.argv[1])
