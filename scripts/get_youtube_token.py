#!/usr/bin/env python3
"""
Brain Beats — Get YouTube OAuth Refresh Token
Run this ONCE locally. Paste the client_id and client_secret from
Google Cloud Console. You'll get a refresh token to add to GitHub Secrets.

Usage: python scripts/get_youtube_token.py
"""

import json
import os
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

CLIENT_ID     = input("Paste your YouTube CLIENT ID: ").strip()
CLIENT_SECRET = input("Paste your YouTube CLIENT SECRET: ").strip()

REDIRECT_URI  = "http://localhost:8080"
SCOPES        = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube"

AUTH_URL = (
    "https://accounts.google.com/o/oauth2/auth"
    f"?client_id={urllib.parse.quote(CLIENT_ID)}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&response_type=code"
    f"&scope={urllib.parse.quote(SCOPES)}"
    "&access_type=offline"
    "&prompt=consent"
)

print(f"\nOpening browser for Google auth...")
print(f"If it doesn't open, visit:\n{AUTH_URL}\n")
webbrowser.open(AUTH_URL)

auth_code = None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        auth_code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h2>Brain Beats: Auth complete! Close this tab.</h2>")
    def log_message(self, *args):
        pass

print("Waiting for Google callback on localhost:8080...")
server = HTTPServer(("", 8080), Handler)
server.handle_request()

if not auth_code:
    print("ERROR: No auth code received."); exit(1)

data = urllib.parse.urlencode({
    "code":          auth_code,
    "client_id":     CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri":  REDIRECT_URI,
    "grant_type":    "authorization_code",
}).encode()

req = urllib.request.Request(
    "https://oauth2.googleapis.com/token",
    data=data,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)
resp = json.loads(urllib.request.urlopen(req).read())

print("\n" + "="*60)
print("BRAIN BEATS — GitHub Secrets (add all 3)")
print("="*60)
print(f"YOUTUBE_CLIENT_ID      = {CLIENT_ID}")
print(f"YOUTUBE_CLIENT_SECRET  = {CLIENT_SECRET}")
print(f"YOUTUBE_REFRESH_TOKEN  = {resp.get('refresh_token', 'ERROR — no refresh token')}")
print("="*60)
print("\nPaste these into: GitHub repo → Settings → Secrets → Actions")
