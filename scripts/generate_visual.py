#!/usr/bin/env python3
"""Generate a looping visual pointer for Brain Beats.

Brain Beats uses dark, minimal visuals — deep space, slow particles,
dark ocean, abstract waveforms. No voice, no text overlays needed
beyond the subtle branding drawtext in compile step.

Usage: python scripts/generate_visual.py 01
"""


import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).parent.parent


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


    src_name = DEFAULT_VISUAL
    for keyword, fname in VISUAL_MAP.items():
        if keyword in benefit:
            src_name = fname
            break


    src = ROOT / "assets" / "visuals" / src_name
    if not src.exists():
        print(f"WARNING: {src_name} not found, falling back to {DEFAULT_VISUAL}")
        src_name = DEFAULT_VISUAL


    out_dir = ROOT / "output" / "visuals"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{row_id}_{freq}.json"


    pointer = {
        "source": f"assets/visuals/{src_name}",
        "loops_to_seconds": dur_s,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(pointer, f, indent=2)


    size_str = f"{src.stat().st_size/1e6:.1f}MB" if src.exists() else "missing"
    print(f"Brain Beats {row_id} | {freq}")
    print(f"  Visual: {src_name}  ({size_str})")
    print(f"  Loops to: {dur_s}s ({dur_h}h)")
    print(f"  Pointer: {out_path}")




if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <row_id>"); sys.exit(1)
    run(sys.argv[1])
