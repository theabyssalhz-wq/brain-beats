#!/usr/bin/env python3
"""Generate Brain Beats thumbnail.

Style inspired by SleepTube + Study Sonic Focus + The Power Of You:
- Deep dark background (near black, slight color tint per frequency)
- Large Hz number centred — the HERO element
- Subtitle benefit text below
- Thin horizontal rule
- Channel name bottom-right
- Subtle radial glow behind Hz number (frequency color)
- Clean, minimal — no clutter

Usage: python scripts/generate_thumbnail.py 01
"""

import csv
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math

ROOT = Path(__file__).parent.parent

W, H = 1280, 720

# Frequency → accent colour (HSL-ish, as RGB)
FREQ_COLORS = {
    "40Hz":    (80, 200, 255),    # electric cyan — focus/gamma
    "432Hz":   (100, 180, 255),   # soft blue — sleep/calm
    "528Hz":   (100, 255, 180),   # emerald green — healing/miracle
    "7.83Hz":  (120, 220, 100),   # earth green — grounding
    "10Hz":    (180, 180, 255),   # lavender — alpha/calm
    "4Hz":     (160, 100, 255),   # deep violet — theta
    "963Hz":   (255, 200, 80),    # gold — divine/pineal
    "174Hz":   (80, 220, 200),    # teal — pain relief
    "396Hz":   (200, 100, 255),   # purple — liberation
    "639Hz":   (255, 120, 160),   # rose — heart chakra
    "852Hz":   (120, 160, 255),   # indigo — third eye
    "2Hz":     (60, 100, 200),    # deep navy — delta sleep
}
DEFAULT_COLOR = (150, 150, 255)

FONT_CANDIDATES = [
    ROOT / "assets" / "fonts" / "bold.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
]


def _get_font(size: int):
    for f in FONT_CANDIDATES:
        if f.exists():
            return ImageFont.truetype(str(f), size)
    return ImageFont.load_default()


def _radial_glow(img: Image.Image, cx: int, cy: int, radius: int, color: tuple, alpha: int = 60):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    steps = 12
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(alpha * (1 - i / steps) ** 1.5)
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(*color, a)
        )
    img.paste(glow, mask=glow)


def run(row_id: str) -> None:
    csv_path = ROOT / "content_plan.csv"
    with open(csv_path, newline="", encoding="utf-8") as f:
        row = next((r for r in csv.DictReader(f) if r["id"] == row_id), None)
    if row is None:
        print(f"ERROR: row {row_id!r} not found", file=sys.stderr); sys.exit(1)

    freq    = row["frequency"]
    benefit = row["benefit"]
    title   = row["title"]
    accent  = FREQ_COLORS.get(freq, DEFAULT_COLOR)

    # --- Background: very dark with faint tinted gradient ---
    bg = Image.new("RGBA", (W, H), (8, 8, 14, 255))
    draw = ImageDraw.Draw(bg)

    # Soft vignette tint
    for y in range(H):
        t = y / H
        r_off = int(accent[0] * 0.04 * (1 - t))
        g_off = int(accent[1] * 0.04 * (1 - t))
        b_off = int(accent[2] * 0.04 * (1 - t))
        draw.line([(0, y), (W, y)], fill=(8 + r_off, 8 + g_off, 14 + b_off, 255))

    img = bg.convert("RGBA")

    # --- Radial glow behind Hz number ---
    _radial_glow(img, W // 2, H // 2 - 40, 340, accent, alpha=90)

    draw = ImageDraw.Draw(img)

    # --- Thin top accent line ---
    draw.rectangle([0, 0, W, 3], fill=(*accent, 200))

    # --- Main Hz number ---
    font_hz  = _get_font(200)
    font_sub = _get_font(52)
    font_ch  = _get_font(32)
    font_rule = _get_font(28)

    hz_text  = freq
    bbox = draw.textbbox((0, 0), hz_text, font=font_hz)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (W - tw) // 2
    ty = (H - th) // 2 - 80

    # Glow shadow pass
    shadow_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_img)
    for off in range(4, 0, -1):
        alpha_s = int(120 / off)
        s_draw.text((tx + off, ty + off), hz_text, font=font_hz, fill=(*accent, alpha_s))
    shadow_blur = shadow_img.filter(ImageFilter.GaussianBlur(radius=8))
    img = Image.alpha_composite(img, shadow_blur)
    draw = ImageDraw.Draw(img)

    # Main Hz text
    draw.text((tx, ty), hz_text, font=font_hz, fill=(*accent, 255))

    # --- Horizontal divider ---
    rule_y = ty + th + 20
    rule_x1 = W // 2 - 160
    rule_x2 = W // 2 + 160
    draw.rectangle([rule_x1, rule_y, rule_x2, rule_y + 2], fill=(*accent, 120))

    # --- Benefit subtitle ---
    sub_text  = benefit.upper()
    bbox2 = draw.textbbox((0, 0), sub_text, font=font_sub)
    sw = bbox2[2] - bbox2[0]
    draw.text(((W - sw) // 2, rule_y + 18), sub_text, font=font_sub,
              fill=(255, 255, 255, 210))

    # --- Channel name bottom right ---
    ch_text = "BRAIN BEATS"
    bbox3 = draw.textbbox((0, 0), ch_text, font=font_ch)
    cw = bbox3[2] - bbox3[0]
    draw.text((W - cw - 40, H - 50), ch_text, font=font_ch,
              fill=(*accent, 180))

    # --- Thin bottom accent line ---
    draw.rectangle([0, H - 3, W, H], fill=(*accent, 180))

    # Output
    out_dir = ROOT / "output" / "thumbnails"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{row_id}_{freq}_thumb.png"
    img.convert("RGB").save(str(out_path), "PNG", optimize=True)

    print(f"Brain Beats {row_id} | {freq}")
    print(f"  Accent: {accent}")
    print(f"  Saved:  {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <row_id>"); sys.exit(1)
    run(sys.argv[1])
