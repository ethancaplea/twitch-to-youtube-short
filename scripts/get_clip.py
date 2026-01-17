import sys
import os
import requests
from datetime import datetime, timedelta

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

print("TOP CLIP FOUND")
print(f"Title: {top_clip['title']}")
print(f"Views: {top_clip['view_count']}")
print(f"URL: {top_clip['url']}")

# --- Download clip ---
import os
import subprocess

# Make sure the clips folder exists
os.makedirs("clips", exist_ok=True)

# Set output path inside the clips folder
output_file = "clips/latest_clip.mp4"

print(f"Downloading clip to {output_file}...")

# Use yt-dlp to download the Twitch clip MP4
subprocess.run([
    "yt-dlp",
    "-f", "best",
    "-o", output_file,
    top_clip["url"]
], check=True)

print("Download complete.")


