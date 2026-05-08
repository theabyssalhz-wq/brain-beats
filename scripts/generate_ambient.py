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
AMBIENT_MAP = {
    "sleep":      "deep_sleep_pad.wav",
    "delta":      "deep_sleep_pad.wav",
    "focus":      "cosmic_focus.wav",
    "study":      "cosmic_focus.wav",
    "adhd":       "cosmic_focus.wav",
    "gamma":      "cosmic_focus.wav",
    "healing":    "healing_drone.wav",
    "chakra":     "healing_drone.wav",
    "heart":      "healing_drone.wav",
    "pineal":     "healing_drone.wav",
    "grounding":  "earth_resonance.wav",
    "earth":      "earth_resonance.wav",
    "schumann":   "earth_resonance.wav",
    "theta":      "theta_dream.wav",
    "meditation": "theta_dream.wav",
    "alpha":      "alpha_calm.wav",
    "calm":       "alpha_calm.wav",
    "anxiety":    "alpha_calm.wav",
    "morning":    "morning_light.wav",
}
DEFAULT_AMBIENT = "healing_drone.wav"




def run(row_id: str) -> None:
    csv_path = ROOT / "content_plan.csv"
    with open(csv_path, newline="", encoding="utf-8") as f:
        row = next((r for r in csv.DictReader(f) if r["id"] == row_id), None)
    if row is None:
        print(f"ERROR: row {row_id!r} not found", file=sys.stderr); sys.exit(1)


    freq    = row["frequency"]
    benefit = row["benefit"].lower()
    dur_h   = int(row.get("duration_hours", 3))
    dur_s   = dur_h * 3600


    src_name = DEFAULT_AMBIENT
    for keyword, fname in AMBIENT_MAP.items():
        if keyword in benefit:
            src_name = fname
            break


    src = ROOT / "assets" / "ambient" / src_name
    if not src.exists():
        print(f"WARNING: {src_name} not found, falling back to {DEFAULT_AMBIENT}")
        src_name = DEFAULT_AMBIENT


    src_full = ROOT / "assets" / "ambient" / src_name
    if not src_full.exists():
        print(f"ERROR: Ambient file missing: {src_full}", file=sys.stderr); sys.exit(1)


    out_dir = ROOT / "output" / "ambient"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{row_id}_{freq}_{dur_h}h_ambient.mp3"


    # Use ffmpeg to loop the source to duration
    cmd = [
        "ffmpeg", "-stream_loop", "-1", "-t", str(dur_s),
        "-i", str(src_full),
        "-ac", "2", "-ar", "44100", "-b:a", "192k",
        str(out_path), "-y"
    ]


    print(f"Brain Beats {row_id} | {freq}")
    print(f"  Ambient: {src_name}")
    print(f"  Target:  {dur_s}s ({dur_h}h)")


    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg failed: {result.stderr}", file=sys.stderr); sys.exit(1)


    print(f"  Done: {out_path.name}")




if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <row_id>"); sys.exit(1)
    run(sys.argv[1])
