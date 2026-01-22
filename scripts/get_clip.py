import sys
import os
import requests
import re
from datetime import datetime, timedelta

def safe_filename(text):
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text.strip("_")[:80]

if len(sys.argv) < 2:
    print("No streamer provided")
    sys.exit(1)

streamer = sys.argv[1]

client_id = os.environ.get("TWITCH_CLIENT_ID")
client_secret = os.environ.get("TWITCH_CLIENT_SECRET")

# Get app access token
token_resp = requests.post(
    "https://id.twitch.tv/oauth2/token",
    params={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
)
token_resp.raise_for_status()
access_token = token_resp.json()["access_token"]

headers = {
    "Client-ID": client_id,
    "Authorization": f"Bearer {access_token}"
}

# Get broadcaster ID
user_resp = requests.get(
    "https://api.twitch.tv/helix/users",
    headers=headers,
    params={"login": streamer}
)
user_resp.raise_for_status()
users = user_resp.json()["data"]
if not users:
    print("Streamer not found")
    sys.exit(1)

broadcaster_id = users[0]["id"]

# Get clips from last 7 days
started_at = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"

clips_resp = requests.get(
    "https://api.twitch.tv/helix/clips",
    headers=headers,
    params={
        "broadcaster_id": broadcaster_id,
        "started_at": started_at,
        "first": 20
    }
)
clips_resp.raise_for_status()
clips = clips_resp.json()["data"]

if not clips:
    print("No clips found")
    sys.exit(0)

top_clip = max(clips, key=lambda c: c["view_count"])

clip_title = top_clip["title"]
game_name = top_clip["game_name"]

print("TOP CLIP FOUND")
print("CLIP_TITLE:", clip_title)
print("GAME_NAME:", game_name)
print(f"Views: {top_clip['view_count']}")
print(f"URL: {top_clip['url']}")

filename_title = safe_filename(clip_title)
filename_game = safe_filename(game_name)

# --- Download clip ---
import os
import subprocess

# Make sure the clips folder exists
os.makedirs("clips", exist_ok=True)

output_file = f"clips/{filename_title}-{filename_game}.mp4"

print(f"Downloading clip to {raw_clip_path}...")

# Use yt-dlp to download the Twitch clip MP4
subprocess.run([
    "yt-dlp",
    "-f", "best",
    "-o", raw_clip_path,
    top_clip["url"]
], check=True)

print("Download complete.")
print(f"CLIP_PATH: {output_file}")



