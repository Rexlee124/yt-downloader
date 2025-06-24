from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for all; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body structure
class VideoRequest(BaseModel):
    url: str

@app.post("/download")
def get_stream_link(data: VideoRequest):
    url = data.url
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'quiet': True,
            'skip_download': True,
            'noplaylist': True,
            'youtube_include_dash_manifest': False,
            'socket_timeout': 10,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

            # Pick best combined audio+video format
            best = None
            for f in formats:
                if f.get('acodec') != 'none' and f.get('vcodec') != 'none':
                    if best is None or (f.get('height') or 0) > (best.get('height') or 0):
                        best = f

            # Fallback if no good match
            if best is None:
                best = max(formats, key=lambda f: f.get('height', 0) or 0)

            video_url = best.get('url')
            return {
                "status": "success",
                "download_url": video_url
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
