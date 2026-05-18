import subprocess
import requests
import base64

YOUTUBE_URL = "https://youtube.com/watch?v=RYhbprsJWUQ"
GITHUB_TOKEN = open("token.txt").read().strip()
REPO = "Codar123/Animal-Planet-"
FILE_PATH = "live.m3u"

# Get fresh m3u8 URL
url = subprocess.check_output(
    ["yt-dlp", "--extractor-args", "youtube:player_client=android", "-g", YOUTUBE_URL],
    text=True
).strip()

# Build m3u content
m3u = f"""#EXTM3U
#EXTINF:-1,Animal Planet
{url}
"""

# Get current file SHA (needed for GitHub API update)
api_url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
headers = {"Authorization": f"token {GITHUB_TOKEN}"}
r = requests.get(api_url, headers=headers)
sha = r.json().get("sha")

# Upload to GitHub
content = base64.b64encode(m3u.encode()).decode()
requests.put(api_url, headers=headers, json={
    "message": "refresh live.m3u",
    "content": content,
    "sha": sha
})

print("Done! live.m3u updated on GitHub.")
