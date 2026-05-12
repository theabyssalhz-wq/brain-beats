
#!/usr/bin/env python3
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

SHORTS_DURATION = 58
W_SHORT, H_SHORT = 1080, 1920

def get_channel_info(benefit: str, freq: str):
    benefit = benefit.lower()
    abyssal_keywords = ["sleep", "delta", "theta", "grounding", "abyssal", "deep", "pain", "fear"]
    if any(k in benefit for k in abyssal_keywords) or freq in ["2Hz", "4Hz", "7.83Hz", "174Hz"]:
        return "ABYSSAL F R E Q U E N C I E S"
    return "BRAIN BEATS"

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
    with open(ROOT / "content_plan.csv", newline="", encoding="utf-8") as f:
        row = next((r for r in csv.DictReader(f) if r["id"] == row_id), None)
    if not row: return

    freq, benefit = row["frequency"], row["benefit"]
    row_idx = int(row_id) - 1
    ch_name = get_channel_info(benefit, freq)

    visualptr = ROOT / "output" / "visuals" / f"{row_id}_{freq}.json"
    pointer = json.loads(visualptr.read_text())
    visual_src = ROOT / pointer["source"]
    binaural = ROOT / "output" / "binaural" / f"{row_id}_{freq}_3h.mp3"

    hook = _get_hook(benefit, row_idx)
    hook_lines = hook.split("\n")
    hook_line1 = hook_lines[0].replace("'", "\\'").replace(":", "\\:")
    hook_line2 = hook_lines[1].replace("'", "\\'").replace(":", "\\:") if len(hook_lines) > 1 else ""

    # Improved Video Filter: Breathing effect + Cinematic overlays
    video_filter = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"zoompan=z='1.1+0.05*sin(2*PI*it/15)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920,"
        f"drawtext=text='{hook_line1}':fontsize=72:fontcolor=white@0.9:shadowcolor=black@0.8:shadowx=3:shadowy=3:x=(w-tw)/2:y=h*0.3"
    )
    if hook_line2:
        video_filter += f",drawtext=text='{hook_line2}':fontsize=72:fontcolor=white@0.9:shadowcolor=black@0.8:shadowx=3:shadowy=3:x=(w-tw)/2:y=h*0.3+90"
    
    video_filter += (
        f",drawtext=text='{freq}':fontsize=50:fontcolor=white@0.5:x=(w-tw)/2:y=h*0.75"
        f",drawtext=text='{ch_name}':fontsize=34:fontcolor=white@0.4:x=w-tw-40:y=h-70"
    )

    out_path = ROOT / "output" / "shorts" / f"{row_id}_{freq}_short.mp4"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-stream_loop", "-1", "-t", str(SHORTS_DURATION), "-i", str(visual_src),
        "-i", str(binaural),
        "-filter_complex", f"[0:v]{video_filter}[v];[1:a]atrim=end={SHORTS_DURATION},afade=t=out:st={SHORTS_DURATION-3}:d=3[a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-t", str(SHORTS_DURATION),
        str(out_path), "-y"
    ]

    subprocess.run(cmd)
    print(f"Short generated: {out_path}")

if __name__ == "__main__":
    run(sys.argv[1])
