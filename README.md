# Brain Beats

Pure frequency. No voice. No distractions.

Automated YouTube channel pipeline — binaural beats, solfeggio frequencies, and ambient soundscapes. Built for long-session meditation, sleep, focus, and healing content.

## Channel Identity

- No voiceover — frequency is the content
- Dark, minimal visual aesthetic (inspired by SleepTube, Study Sonic Focus, The Power Of You)
- Clean Hz-hero thumbnails with frequency accent colours
- UGC-style Shorts with hook text overlays
- Videos: 1h / 2h / 3h / 8h depending on type

## Pipeline

```
generate_visual.py       →  picks looping visual per frequency
generate_thumbnail.py    →  dark Hz-hero thumbnail (Pillow)
generate_ambient.py      →  loops ambient pad to full duration
generate_binaural.py     →  pure sine wave binaural tones
generate_description.py  →  SEO description + YouTube chapters
compile_video.py         →  muxes visual + binaural + ambient
generate_shorts.py       →  58s vertical Short with UGC hook text
upload_youtube.py        →  resumable upload + thumbnail set
```

## Assets Required

Place in `assets/` before running:

```
assets/
  visuals/
    dark_nebula.mp4      ← sleep / delta
    particles_cyan.mp4   ← focus / gamma
    deep_cosmos.mp4      ← healing / default
    golden_cosmos.mp4    ← pineal / 963Hz
    earth_pulse.mp4      ← grounding / Schumann
    void_ripple.mp4      ← theta / meditation
    soft_void.mp4        ← alpha / calm
    dawn_light.mp4       ← morning
  ambient/
    deep_sleep_pad.mp3
    cosmic_focus.mp3
    healing_drone.mp3
    earth_resonance.mp3
    theta_dream.mp3
    alpha_calm.mp3
    morning_light.mp3
  fonts/
    bold.ttf             ← optional (falls back to DejaVuSans)
```

## GitHub Secrets Required

```
YOUTUBE_CLIENT_ID
YOUTUBE_CLIENT_SECRET
YOUTUBE_REFRESH_TOKEN
```

Get your refresh token: `python scripts/get_youtube_token.py` (run locally once)

## Run

Trigger the workflow manually in GitHub Actions → Render Brain Beats video → enter video ID (01–15).

Enable `upload_to_youtube: true` to auto-publish when the render completes.
