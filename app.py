from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.post("/info")
def get_video_info(data: VideoRequest):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url, download=False)
            formats = [
                {
                    "format_id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "resolution": f.get("resolution") or f"{f.get('height', 'N/A')}p",
                    "url": f.get("url"),
                    "filesize": f.get("filesize", 0)
                }
                for f in info.get("formats", [])
                if f.get("acodec") != "none" and f.get("vcodec") != "none" and f.get("url")
            ]

        return {
            "status": "success",
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "formats": formats
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
