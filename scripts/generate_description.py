
#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

def get_channel_info(benefit: str, freq: str):
    benefit = benefit.lower()
    abyssal_keywords = ["sleep", "delta", "theta", "grounding", "abyssal", "deep", "pain", "fear"]
    if any(k in benefit for k in abyssal_keywords) or freq in ["2Hz", "4Hz", "7.83Hz", "174Hz"]:
        return "ABYSSAL F R E Q U E N C I E S", "@AbyssalFrequencies"
    return "BRAIN BEATS", "@BrainBeatsFrequency"

def run(row_id: str):
    with open(ROOT / "content_plan.csv", newline="", encoding="utf-8") as f:
        row = next((r for r in csv.DictReader(f) if r["id"] == row_id), None)
    if not row: return

    freq, benefit, title = row["frequency"], row["benefit"], row["title"]
    ch_name, handle = get_channel_info(benefit, freq)
    
    description = f"""{title}

Dive into the depth of {freq}. Pure, uninterrupted frequency designed for {benefit.lower()}.

No distractions. No voice. Just the vibration.

─────────────────────────────────────
THE SCIENCE OF {freq}
─────────────────────────────────────
{freq} is a precision-tuned frequency known for its ability to resonate with the brain's natural rhythms. Whether you are seeking deep focus, restorative sleep, or emotional release, this session provides a clean, professional-grade audio environment for your practice.

BENEFITS:
✦ Deep {benefit}
✦ Cognitive realignment
✦ Stress reduction
✦ Pure frequency immersion

─────────────────────────────────────
HOW TO LISTEN
─────────────────────────────────────
Best experienced with stereo headphones at a comfortable volume. Allow the frequency to become the background of your consciousness.

Duration: {row.get('duration_hours', '3')} Hours
Channel: {ch_name}

Subscribe for more frequencies: https://youtube.com/{handle}

#binauralbeats #healingfrequency #{freq.replace('.','')} #meditation #{benefit.replace(' ','')}
"""
    out_path = ROOT / "output" / "descriptions" / f"{row_id}_{freq}_description.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(description)
    print(f"Description saved: {out_path}")

if __name__ == "__main__":
    run(sys.argv[1])
