import subprocess

YOUTUBE_URL = "https://youtube.com/watch?v=RYhbprsJWUQ"

url = subprocess.check_output(
    [
        "yt-dlp",
        "--cookies", "cookies.txt",
        "-g",
        YOUTUBE_URL
    ],
    text=True
).strip()

m3u = f"""#EXTM3U
#EXTINF:-1,Animal Planet
{url}
"""

with open("live.m3u", "w") as f:
    f.write(m3u)
