#!/usr/bin/env python3
"""Upload Brain Beats video to YouTube.

Reads: output/videos/{id}_{freq}_{dur_h}h.mp4
       output/thumbnails/{id}_{freq}_thumb.png
       output/descriptions/{id}_{freq}_description.txt

Usage: python scripts/upload_youtube.py 01 [public|unlisted|private]
"""

import csv
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).parent.parent

TOKEN_URL  = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
CHUNK_SIZE = 10 * 1024 * 1024
CATEGORY_ID = "22"


def _get_token() -> str:
    r = requests.post(TOKEN_URL, data={
        "grant_type":     "refresh_token",
        "refresh_token":  os.environ["YOUTUBE_REFRESH_TOKEN"],
        "client_id":      os.environ["YOUTUBE_CLIENT_ID"],
        "client_secret":  os.environ["YOUTUBE_CLIENT_SECRET"],
    })
    r.raise_for_status()
    return r.json()["access_token"]


def _resumable_upload(token: str, meta: dict, video_path: Path) -> str:
    size = video_path.stat().st_size
    r = requests.post(UPLOAD_URL, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": "video/mp4",
        "X-Upload-Content-Length": str(size),
    }, json=meta)
    r.raise_for_status()
    uri = r.headers["Location"]

    uploaded = 0
    with open(video_path, "rb") as f:
        while uploaded < size:
            chunk = f.read(CHUNK_SIZE)
            end   = uploaded + len(chunk) - 1
            resp  = requests.put(uri, headers={
                "Content-Range": f"bytes {uploaded}-{end}/{size}",
                "Content-Type": "video/mp4",
            }, data=chunk)
            if resp.status_code in (200, 201):
                return resp.json()["id"]
            elif resp.status_code == 308:
                uploaded = int(resp.headers.get("Range", f"bytes=0-{end}").split("-")[1]) + 1
                print(f"  {uploaded/1e6:.0f}MB / {size/1e6:.0f}MB ({uploaded/size*100:.0f}%)")
            else:
                print(f"Upload error {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
                sys.exit(1)
    raise RuntimeError("Upload ended unexpectedly")


def _set_thumbnail(token: str, vid_id: str, thumb: Path):
    with open(thumb, "rb") as f:
        r = requests.post(
            f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid_id}&uploadType=media",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "image/png"},
            data=f.read()
        )
    print(f"  Thumbnail: {'✓' if r.status_code==200 else r.status_code}")


def run(row_id: str, privacy: str = "public") -> None:
    with open(ROOT / "content_plan.csv", newline="", encoding="utf-8") as f:
        row = next((r for r in csv.DictReader(f) if r["id"] == row_id), None)
    if not row:
        print(f"ERROR: row {row_id!r} not found", file=sys.stderr); sys.exit(1)

    freq  = row["frequency"]
    dur_h = int(row.get("duration_hours", 3))
    tags  = [t.strip() for t in row["tags"].split(",") if t.strip()]

    video = ROOT / "output" / "videos"      / f"{row_id}_{freq}_{dur_h}h.mp4"
    thumb = ROOT / "output" / "thumbnails"  / f"{row_id}_{freq}_thumb.png"
    desc  = ROOT / "output" / "descriptions"/ f"{row_id}_{freq}_description.txt"

    if not video.exists():
        print(f"ERROR: video not found: {video}", file=sys.stderr); sys.exit(1)

    print(f"Uploading Brain Beats {row_id} | {freq} | {video.stat().st_size/1e9:.2f}GB")

    token = _get_token()
    meta  = {
        "snippet": {
            "title":       row["title"],
            "description": desc.read_text(encoding="utf-8") if desc.exists() else row["title"],
            "tags":        tags,
            "categoryId":  CATEGORY_ID,
            "defaultLanguage": "en",
        },
        "status": {"privacyStatus": privacy, "madeForKids": False},
    }

    vid_id = _resumable_upload(token, meta, video)
    print(f"  Uploaded ✓  https://youtube.com/watch?v={vid_id}")

    if thumb.exists():
        _set_thumbnail(token, vid_id, thumb)

    result = {"video_id": vid_id, "url": f"https://youtube.com/watch?v={vid_id}",
              "row_id": row_id, "frequency": freq, "privacy": privacy}
    out = ROOT / "output" / f"{row_id}_upload_result.json"
    out.write_text(json.dumps(result, indent=2))
    print(f"  Result saved: {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <row_id> [public|unlisted|private]"); sys.exit(1)
    privacy = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in ("public","unlisted","private") else "public"
    run(sys.argv[1], privacy)
