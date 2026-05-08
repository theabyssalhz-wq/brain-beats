#!/usr/bin/env python3
"""Generate SEO YouTube descriptions for Brain Beats.

Pure frequency channel — no voice. Description style mirrors
The Power Of You: poetic, minimal, science-backed.

Usage: python scripts/generate_description.py 01
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CHANNEL = "Brain Beats"
HANDLE  = "@BrainBeatsFrequency"

FREQ_DATA = {
    "40Hz": {
        "hook": "Your brain produces 40Hz Gamma waves during states of peak focus and heightened awareness.",
        "science": "MIT and Harvard research has linked 40Hz stimulation to enhanced memory consolidation, faster information processing, and reduced cognitive fatigue. Gamma waves are the fastest brainwave state — the operating frequency of a brain firing on all cylinders.",
        "benefits": ["Deep, sustained focus — no stimulants", "Memory and information retention", "Mental clarity and processing speed", "Flow state activation"],
        "listen": "Best with stereo headphones. Use during study, deep work, reading, or any task requiring peak mental output. Volume at a comfortable level — this is meant to run in the background.",
        "chapters": ["0:00 Brain Activation", "10:00 Gamma Entrainment", "30:00 Deep Focus Zone", "1:00:00 Flow State", "2:00:00 Peak Performance"],
    },
    "432Hz": {
        "hook": "432Hz resonates with the mathematical patterns found throughout nature — from the spiral of galaxies to the structure of DNA.",
        "science": "Unlike the modern standard of 440Hz, 432Hz tuning aligns with the Schumann Resonance (Earth's natural electromagnetic frequency at ~7.83Hz) and appears in sacred geometry across ancient cultures. Many musicians and researchers report a noticeably warmer, more grounding listening experience.",
        "benefits": ["Deep, restorative sleep", "Natural cortisol reduction", "Nervous system downregulation", "Alignment with natural frequency patterns"],
        "listen": "No headphones required for relaxation. For the full binaural effect, use stereo headphones. Best during sleep or before bed.",
        "chapters": ["0:00 Settling In", "15:00 Sleep Descent", "30:00 Delta Zone", "1:00:00 Deep Sleep", "2:00:00 Full Body Reset"],
    },
    "528Hz": {
        "hook": "528Hz is used by biochemists to repair DNA. It is the exact frequency used to repair genetic defects according to Dr. Leonard Horowitz.",
        "science": "Part of the ancient Solfeggio scale, 528Hz sits at the heart of the electromagnetic light spectrum visible to the human eye. It has been associated with transformation, emotional healing, and cellular repair — earning its name as the 'Miracle Tone'.",
        "benefits": ["Cellular healing and DNA repair", "Emotional transformation", "Positive energy amplification", "Stress and anxiety reduction"],
        "listen": "Stereo headphones enhance the binaural effect. Sit or lie comfortably. Set an intention before pressing play.",
        "chapters": ["0:00 Intention Setting", "10:00 Miracle Tone Begins", "30:00 Cellular Resonance", "1:00:00 Deep Healing Phase", "2:00:00 Full Body Repair"],
    },
    "7.83Hz": {
        "hook": "7.83Hz is the heartbeat of the Earth. Every living thing on this planet evolved within this frequency field.",
        "science": "The Schumann Resonance — discovered by physicist Winfried Schumann in 1952 — is the electromagnetic frequency produced by lightning strikes resonating in the cavity between the Earth's surface and the ionosphere. Modern EMF pollution from devices has disrupted our natural entrainment to this frequency.",
        "benefits": ["Nervous system reset", "Anxiety and stress dissolution", "Deep earthing effect", "Reconnection to natural rhythms"],
        "listen": "Ideal lying down or seated on the floor. Go barefoot if possible. Let everything go.",
        "chapters": ["0:00 Earthing Arrival", "10:00 Resonance Begins", "30:00 Nervous System Reset", "1:00:00 Deep Grounding", "2:00:00 Earth Frequency Immersion"],
    },
    "DEFAULT": {
        "hook": "This frequency has been used in ancient sound healing practices and is now being studied by modern researchers.",
        "science": "Solfeggio frequencies are a set of ancient musical tones with roots in Gregorian chanting and early sacred music. Each frequency is associated with specific physical, emotional, and spiritual effects that are now being investigated in modern neuroscience and bioacoustics research.",
        "benefits": ["Deep meditation", "Healing and restoration", "Stress and anxiety relief", "Energetic realignment"],
        "listen": "Stereo headphones recommended. Find a comfortable position and allow yourself to receive.",
        "chapters": ["0:00 Arrival", "15:00 Frequency Deepens", "30:00 Healing Phase", "1:00:00 Full Immersion", "2:00:00 Deep State"],
    },
}

# Additional entries for all other frequencies
FREQ_DATA["4Hz"]   = FREQ_DATA["DEFAULT"] | {"hook": "4Hz Theta waves appear in the brain during deep meditation, light sleep, and moments of profound creativity."}
FREQ_DATA["10Hz"]  = FREQ_DATA["DEFAULT"] | {"hook": "10Hz Alpha waves are the brain's natural resting rhythm — the bridge between conscious thought and deep relaxation."}
FREQ_DATA["963Hz"] = FREQ_DATA["DEFAULT"] | {"hook": "963Hz is associated with the pineal gland — the 'seat of the soul' in many spiritual traditions — and the highest Solfeggio frequency."}
FREQ_DATA["174Hz"] = FREQ_DATA["DEFAULT"] | {"hook": "174Hz is the lowest of the Solfeggio tones, known as a natural anesthetic. It reduces physical and energetic pain without medication."}
FREQ_DATA["396Hz"] = FREQ_DATA["DEFAULT"] | {"hook": "396Hz liberates you from fear and guilt — the two most destructive emotional frequencies in the human energy field."}
FREQ_DATA["639Hz"] = FREQ_DATA["DEFAULT"] | {"hook": "639Hz is the frequency of the heart — connection, love, understanding, and harmony between people."}
FREQ_DATA["852Hz"] = FREQ_DATA["DEFAULT"] | {"hook": "852Hz awakens intuition and inner sight. It replaces negative thoughts with positive ones and opens the third eye."}
FREQ_DATA["2Hz"]   = FREQ_DATA["432Hz"]  | {"hook": "2Hz Delta waves are the deepest brainwave state — only reached in the most profound dreamless sleep and deep meditation."}


def build_description(row: dict) -> str:
    freq    = row["frequency"]
    title   = row["title"]
    benefit = row["benefit"]
    tags    = row.get("tags", "")
    dur_h   = row.get("duration_hours", "3")

    fd = FREQ_DATA.get(freq, FREQ_DATA["DEFAULT"])
    benefits_block  = "\n".join(f"  ✦ {b}" for b in fd["benefits"])
    chapters_block  = "\n".join(fd["chapters"])
    tag_list        = " ".join(f"#{t.strip().replace(' ','')}" for t in tags.split(",")[:12])

    return f"""{fd['hook']}

No voice. No distractions. Pure frequency.

─────────────────────────────────────
{freq} | {benefit.upper()}
─────────────────────────────────────

{fd['science']}

WHAT YOU MAY EXPERIENCE:
{benefits_block}

─────────────────────────────────────
HOW TO LISTEN
─────────────────────────────────────

{fd['listen']}

Duration: {dur_h} hour{'s' if str(dur_h) != '1' else ''} of continuous, uninterrupted frequency.

─────────────────────────────────────
CHAPTERS
─────────────────────────────────────

{chapters_block}

─────────────────────────────────────
ABOUT BRAIN BEATS
─────────────────────────────────────

Brain Beats creates precision-tuned binaural beat sessions — crafted from pure sine wave tones, authentic solfeggio frequencies, and layered ambient soundscapes. No voice. No filler. Just frequency.

Subscribe: https://youtube.com/{HANDLE}

─────────────────────────────────────
DISCLAIMER: For relaxation purposes only. Not a substitute for medical treatment. Consult a doctor if you have epilepsy or use a pacemaker.
─────────────────────────────────────

{tag_list} #brainbeats #binauralbeats #healingfrequency #frequencyhealing #meditationmusic"""


def run(row_id: str) -> None:
    with open(ROOT / "content_plan.csv", newline="", encoding="utf-8") as f:
        row = next((r for r in csv.DictReader(f) if r["id"] == row_id), None)
    if row is None:
        print(f"ERROR: row {row_id!r} not found", file=sys.stderr); sys.exit(1)

    freq = row["frequency"]
    desc = build_description(row)

    out_dir = ROOT / "output" / "descriptions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{row_id}_{freq}_description.txt"
    out_path.write_text(desc, encoding="utf-8")
    print(f"Brain Beats {row_id} | {freq}")
    print(f"  Description: {out_path}  ({len(desc)} chars)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <row_id>"); sys.exit(1)
    run(sys.argv[1])
