import subprocess
import threading
import time
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

YOUTUBE_URL   = "https://www.youtube.com/live/RYhbprsJWUQ"
REFRESH_EVERY = 2 * 60 * 60  # 2 hours
PORT          = int(os.environ.get("PORT", 8080))
CHANNEL_NAME  = "Animal Planet"

current_stream_url = None
last_refresh       = None
lock               = threading.Lock()


def refresh_url():
    global current_stream_url, last_refresh
    print(f"[{time.strftime('%H:%M:%S')}] Refreshing stream URL...")
    try:
        result = subprocess.run(
            ["yt-dlp", "-g", "--no-warnings", YOUTUBE_URL],
            capture_output=True, text=True, timeout=60
        )
        urls = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
        m3u8_urls = [u for u in urls if "m3u8" in u or "manifest" in u]
        chosen = m3u8_urls[0] if m3u8_urls else (urls[0] if urls else None)
        if chosen:
            with lock:
                current_stream_url = chosen
                last_refresh = time.time()
            print(f"[{time.strftime('%H:%M:%S')}] Stream URL refreshed!")
            return True
        else:
            print(f"[ERROR] No URL returned. stderr: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def refresh_loop():
    while True:
        time.sleep(REFRESH_EVERY)
        refresh_url()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/animal_planet.m3u8":
            with lock:
                url = current_stream_url
            if not url:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b"Stream not ready yet, try again in 30 seconds.")
                return
            m3u8 = (
                f"#EXTM3U\n"
                f"#EXTINF:-1 tvg-name=\"{CHANNEL_NAME}\" group-title=\"Nature\","
                f"{CHANNEL_NAME}\n"
                f"{url}\n"
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.apple.mpegurl")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(m3u8.encode())
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            with lock:
                url = current_stream_url
            status = "Running" if url else "Loading..."
            self.wfile.write(f"""<html><body style='font-family:sans-serif;padding:20px'>
<h2>Animal Planet Proxy</h2>
<p>Status: <b>{status}</b></p>
<p>Add this URL to Televizo:</p>
<code style='background:#eee;padding:8px;display:block'>
YOUR_RENDER_URL/animal_planet.m3u8
</code>
</body></html>""".encode())
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    refresh_url()
    threading.Thread(target=refresh_loop, daemon=True).start()
    print(f"Server running on port {PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
