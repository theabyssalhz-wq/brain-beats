#!/usr/bin/env python3
"""Generate Brain Beats Shorts / Reels — UGC-style text overlays.

No actual UGC footage needed. We simulate it with:
- Dark background with the Hz glow visual (looped 60s clip)
- Large bold hook text that reads like a real person's experience
- Subtitle frequency info
- Vertical 9:16 crop
- 58 seconds (optimal for Shorts algorithm)

This mimics the UGC text-on-screen style without any real face/voice.

Usage: python scripts/generate_shorts.py 01
"""

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

SHORTS_DURATION = 58
W_SHORT, H_SHORT = 1080, 1920

_FONT_CANDIDATES = [
    ROOT / "assets" / "fonts" / "bold.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
]
FONT_PATH = next((str(p) for p in _FONT_CANDIDATES if p.exists()), None)
FP = f"fontfile={FONT_PATH}:" if FONT_PATH else ""

# UGC-style hooks — rotated per video
UGC_HOOKS = {
    "focus":      ["I studied for 4 hours straight.", "My brain wouldn't stop.\nThis fixed it.", "ADHD brain?\nTry this for 10 min."],
    "sleep":      ["Fell asleep in 8 minutes.", "Couldn't sleep for 3 days.\nThis changed that.", "Play this tonight.\nThank me tomorrow."],
    "healing":    ["Something shifted after 20 min.", "I cried. Then felt amazing.", "This frequency hits different."],
    "grounding":  ["I felt the anxiety leave my body.", "10 minutes. Completely reset.", "Earth's frequency. For real."],
    "theta":      ["My mind went completely quiet.", "Deepest meditation I've had.", "I didn't think that was possible."],
    "alpha":      ["Stress is gone. Just... gone.", "Play this in the background.", "I use this every single day."],
    "pineal":     ["Something opened up.", "I don't know what happened\nbut I felt it.", "Try it once. Just try it."],
    "morning":    ["Started my day with this.", "5 minutes. Completely different day.", "This is my morning ritual now."],
    "default":    ["This frequency is wild.", "I wasn't expecting that.", "Try this for 10 minutes."],
}


def _get_hook(benefit: str, video_idx: int) -> str:
    b = benefit.lower()
    for key in UGC_HOOKS:
        if key in b:
            hooks = UGC_HOOKS[key]
            return hooks[video_idx % len(hooks)]
    return UGC_HOOKS["default"][video_idx % len(UGC_HOOKS["default"])]


def run(row_id: str) -> None:
    csv_path = ROOT / "content_plan.csv"
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        row = next((r for r in rows if r["id"] == row_id), None)
    if row is None:
        print(f"ERROR: row {row_id!r} not found", file=sys.stderr); sys.exit(1)

    freq     = row["frequency"]
    benefit  = row["benefit"]
    dur_h    = int(row.get("duration_hours", 3))
    row_idx  = int(row_id) - 1

    # Visual source
    visualptr = ROOT / "output" / "visuals" / f"{row_id}_{freq}.json"
    if not visualptr.exists():
        print(f"ERROR: visual pointer missing", file=sys.stderr); sys.exit(1)
    pointer    = json.loads(visualptr.read_text())
    visual_src = ROOT / pointer["source"]

    # Audio: first 58s of binaural
    binaural = ROOT / "output" / "binaural" / f"{row_id}_{freq}_{dur_h}h.mp3"
    if not binaural.exists():
        print(f"ERROR: binaural missing", file=sys.stderr); sys.exit(1)

    hook = _get_hook(benefit, row_idx)
    hook_esc  = hook.replace("'", "\\'").replace(":", "\\:").replace("\n", "\n")
    freq_esc  = freq.replace("'", "\\'")
    ch_esc    = "BRAIN BEATS"

    # Escape newlines for drawtext: use line break via multiple drawtext or \n
    hook_lines = hook.split("\n")
    hook_line1 = hook_lines[0].replace("'", "\\'").replace(":", "\\:")
    hook_line2 = hook_lines[1].replace("'", "\\'").replace(":", "\\:") if len(hook_lines) > 1 else ""

    # Build drawtext chain
    dt_hook1 = (
        f"[base]drawtext=text='{hook_line1}':"
        f"{FP}fontsize=72:fontcolor=white@0.95:"
        f"shadowcolor=black@0.8:shadowx=3:shadowy=3:"
        f"x=(W-tw)/2:y=H*0.28[h1]"
    )
    if hook_line2:
        dt_hook2 = (
            f"[h1]drawtext=text='{hook_line2}':"
            f"{FP}fontsize=72:fontcolor=white@0.95:"
            f"shadowcolor=black@0.8:shadowx=3:shadowy=3:"
            f"x=(W-tw)/2:y=H*0.28+90[h2]"
        )
        after_hook = "[h2]"
    else:
        dt_hook2 = ""
        after_hook = "[h1]"

    dt_freq = (
        f"{after_hook}drawtext=text='{freq_esc}':"
        f"{FP}fontsize=48:fontcolor=white@0.60:"
        f"shadowcolor=black@0.5:shadowx=2:shadowy=2:"
        f"x=(W-tw)/2:y=H*0.75[freq_t]"
    )
    dt_ch = (
        f"[freq_t]drawtext=text='{ch_esc}':"
        f"{FP}fontsize=34:fontcolor=white@0.50:"
        f"x=W-tw-40:y=H-70[v]"
    )

    filters = [
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,fps=30,format=yuv420p[base]",
        dt_hook1,
    ]
    if dt_hook2:
        filters.append(dt_hook2)
    filters += [dt_freq, dt_ch]

    video_graph = ";".join(filters)
    audio_graph = f"[1:a]atrim=end={SHORTS_DURATION},afade=t=out:st={SHORTS_DURATION-3}:d=3[a]"
    full_graph  = video_graph + ";" + audio_graph

    out_dir = ROOT / "output" / "shorts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{row_id}_{freq}_short.mp4"

    cmd = [
        "ffmpeg",
        "-stream_loop", "-1", "-t", str(SHORTS_DURATION), "-i", str(visual_src),
        "-i", str(binaural),
        "-filter_complex", full_graph,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-t", str(SHORTS_DURATION),
        str(out_path), "-y"
    ]

    print(f"Brain Beats {row_id} | {freq} Short")
    print(f"  Hook: {hook_lines[0]}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg error:\n{result.stderr[-400:]}", file=sys.stderr); sys.exit(1)

    size_mb = out_path.stat().st_size / 1e6
    print(f"  Done. {out_path.name} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <row_id>"); sys.exit(1)
    run(sys.argv[1])
