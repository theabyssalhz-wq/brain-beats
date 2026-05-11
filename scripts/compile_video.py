
#!/usr/bin/env python3
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

def get_channel_info(benefit: str, freq: str):
    benefit = benefit.lower()
    abyssal_keywords = ["sleep", "delta", "theta", "grounding", "abyssal", "deep", "pain", "fear"]
    if any(k in benefit for k in abyssal_keywords) or freq in ["2Hz", "4Hz", "7.83Hz", "174Hz"]:
        return "ABYSSAL F R E Q U E N C I E S", (0, 255, 255) # Teal
    return "BRAIN BEATS", (255, 0, 255) # Magenta

def run(row_id: str):
    with open(ROOT / "content_plan.csv", newline="", encoding="utf-8") as f:
        row = next((r for r in csv.DictReader(f) if r["id"] == row_id), None)
    if not row: return

    freq, benefit = row["frequency"], row["benefit"]
    dur_h = int(row.get("duration_hours", 3))
    dur_s = dur_h * 3600
    ch_name, accent_rgb = get_channel_info(benefit, freq)

    binaural = ROOT / "output" / "binaural" / f"{row_id}_{freq}_{dur_h}h.mp3"
    ambient = ROOT / "output" / "ambient" / f"{row_id}_{freq}_{dur_h}h_ambient.mp3"
    visualptr = ROOT / "output" / "visuals" / f"{row_id}_{freq}.json"
    
    pointer = json.loads(visualptr.read_text())
    visual_src = ROOT / pointer["source"]
    
    # Video Filter: Pulsing effect + Branding
    video_filter = (
        f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
        f"zoompan=z='1.05+0.05*sin(2*PI*it/20)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080,"
        f"drawtext=text='{freq}':fontcolor=white@0.15:fontsize=80:x=(w-tw)/2:y=(h-th)/2,"
        f"drawtext=text='{ch_name}':fontcolor=white@0.4:fontsize=30:x=w-tw-50:y=h-th-50"
    )

    audio_inputs = ["-i", str(binaural)]
    if ambient.exists():
        audio_inputs += ["-i", str(ambient)]
        audio_filter = "[1:a]volume=-3dB[bin];[2:a]volume=-18dB[amb];[bin][amb]amix=inputs=2:duration=longest[a]"
    else:
        audio_filter = "[1:a]volume=-3dB[a]"

    out_path = ROOT / "output" / "videos" / f"{row_id}_{freq}_{dur_h}h.mp4"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-stream_loop", "-1", "-t", str(dur_s), "-i", str(visual_src),
        *audio_inputs,
        "-filter_complex", f"[0:v]{video_filter}[v];{audio_filter}",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-t", str(dur_s),
        str(out_path), "-y"
    ]
    
    subprocess.run(cmd)
    print(f"Video compiled: {out_path}")

if __name__ == "__main__":
    run(sys.argv[1])
