#!/usr/bin/env python3
"""Compile final Brain Beats video.

Brain Beats = binaural (centrepiece) + ambient pad (background) + looped visual.
No voiceover. Clean branding overlay: Hz + channel name only.

Usage: python scripts/compile_video.py 01
"""

import csv
import json
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

CHANNEL_NAME = "Brain Beats"
FONT_COLOR   = "white"
HZ_SIZE      = 64
CH_SIZE      = 32

_FONT_CANDIDATES = [
    ROOT / "assets" / "fonts" / "bold.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    Path("/System/Library/Fonts/Helvetica.ttc"),
]
FONT_PATH = next((str(p) for p in _FONT_CANDIDATES if p.exists()), None)

# Audio levels
BINAURAL_DB = -3     # binaural is the hero
AMBIENT_DB  = -18    # ambient is the canvas


def _probe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True
    )
    if r.returncode != 0 or not r.stdout.strip():
        print(f"ERROR: ffprobe failed on {path}", file=sys.stderr); sys.exit(1)
    return float(r.stdout.strip())


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

    binaural  = ROOT / "output" / "binaural"  / f"{row_id}_{freq}_{dur_h}h.mp3"
    ambient   = ROOT / "output" / "ambient"   / f"{row_id}_{freq}_{dur_h}h_ambient.mp3"
    visualptr = ROOT / "output" / "visuals"   / f"{row_id}_{freq}.json"

    for label, path in [("binaural", binaural), ("visual pointer", visualptr)]:
        if not path.exists():
            print(f"ERROR: {label} missing: {path}", file=sys.stderr); sys.exit(1)

    pointer    = json.loads(visualptr.read_text())
    visual_src = ROOT / pointer["source"]
    have_ambient = ambient.exists()

    print(f"Brain Beats {row_id} | {freq} | {dur_h}h")
    print(f"  Visual:   {visual_src.name}")
    print(f"  Binaural: {binaural.name}")
    print(f"  Ambient:  {ambient.name if have_ambient else '(none)'}")
    print(f"  Font:     {FONT_PATH or 'default'}")

    # Escape for drawtext
    hz_esc = freq.replace(":", "\\:").replace("'", "\\'")
    ch_esc = CHANNEL_NAME.replace(":", "\\:").replace("'", "\\'")
    fp = f"fontfile={FONT_PATH}:" if FONT_PATH else ""

    # Video filter
    video_graph = (
        f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,"
        f"crop=1920:1080,fps=24,format=yuv420p[base];"
        f"[base]drawtext=text='{hz_esc}':"
        f"{fp}fontsize={HZ_SIZE}:fontcolor={FONT_COLOR}@0.12:"
        f"shadowcolor=black@0.1:shadowx=1:shadowy=1:"
        f"x=(W-tw)/2:y=(H-th)/2[mid];"
        f"[mid]drawtext=text='{ch_esc}':"
        f"{fp}fontsize={CH_SIZE}:fontcolor={FONT_COLOR}@0.55:"
        f"shadowcolor=black@0.4:shadowx=1:shadowy=1:"
        f"x=W-tw-40:y=H-th-30[v]"
    )

    # Audio filter — binaural + optional ambient
    if have_ambient:
        audio_graph = (
            f"[1:a]volume={BINAURAL_DB}dB[bin];"
            f"[2:a]volume={AMBIENT_DB}dB[amb];"
            f"[bin][amb]amix=inputs=2:duration=longest:normalize=0[a]"
        )
        inputs_audio = ["-i", str(binaural), "-i", str(ambient)]
    else:
        audio_graph = f"[1:a]volume={BINAURAL_DB}dB[a]"
        inputs_audio = ["-i", str(binaural)]

    full_graph = video_graph + ";" + audio_graph

    out_dir  = ROOT / "output" / "videos"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{row_id}_{freq}_{dur_h}h.mp4"

    cmd = [
        "ffmpeg",
        "-stream_loop", "-1", "-t", str(dur_s), "-i", str(visual_src),
        *inputs_audio,
        "-filter_complex", full_graph,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-pix_fmt", "yuv420p", "-r", "24",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-movflags", "+faststart",
        "-t", str(dur_s),
        "-progress", "pipe:1", "-stats_period", "60",
        str(out_path), "-y"
    ]

    print(f"\nEncoding {dur_h}h video...")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"FFmpeg failed", file=sys.stderr); sys.exit(1)

    size_gb = out_path.stat().st_size / 1e9
    print(f"\nDone. {out_path.name} ({size_gb:.2f} GB)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <row_id>"); sys.exit(1)
    run(sys.argv[1])
