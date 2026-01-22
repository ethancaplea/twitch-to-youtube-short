import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --------------------------
# Check arguments
# --------------------------
if len(sys.argv) < 2:
    print("Usage: python upload_youtube.py <video_file>")
    sys.exit(1)

video_file = sys.argv[1]

if not os.path.exists(video_file):
    print(f"Error: File '{video_file}' does not exist.")
    sys.exit(1)

# --------------------------
# Get secrets from environment
# --------------------------
CLIENT_ID = os.environ.get("JYNXZI_YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("JYNXZI_YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("JYNXZI_YOUTUBE_REFRESH_TOKEN")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    print("Error: Missing one of the required YouTube secrets.")
    sys.exit(1)


# --------------------------
# Create credentials object
# --------------------------
creds = Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    token_uri="https://oauth2.googleapis.com/token"
)

# --------------------------
# Build the YouTube API client
# --------------------------
youtube = build("youtube", "v3", credentials=creds)

# --------------------------
# Derive YouTube title from filename
# --------------------------
filename = os.path.basename(video_file)
title = os.path.splitext(filename)[0]

# Convert underscores back to spaces for readability
title = title.replace("_", " ")

print("Final YouTube title:", title)

# --------------------------
# Upload the video
# --------------------------
request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": title,
            "description": "Automated upload from Twitch clips",
            "tags": ["Twitch", "Shorts"],
            "categoryId": "20"  # Gaming
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    },
    media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
)

print(f"Uploading {video_file} to YouTube...")

response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f"Upload progress: {int(status.progress() * 100)}%")

print("Upload complete!")
print("Video ID:", response["id"])
