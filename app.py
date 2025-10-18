from fastapi import FastAPI, Request, Query
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from downloader import download_youtube_video, download_youtube_audio
import os

app = FastAPI()

# Allow all origins for simplicity during development and deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NEW: SERVE THE FRONTEND ---
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    This endpoint serves the main HTML file to the user.
    """
    # Ensure the path to your index.html is correct
    html_file_path = 'index.html'
    if os.path.exists(html_file_path):
        with open(html_file_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return JSONResponse({"error": "index.html not found"}, status_code=404)

@app.get("/download/video")
async def download_video_endpoint(url: str = Query(...), quality: str = Query("720p")):
    try:
        file_path = download_youtube_video(url, quality)
        if file_path and os.path.exists(file_path):
            return FileResponse(file_path, filename=os.path.basename(file_path), media_type='application/octet-stream')
        else:
            return JSONResponse({"error": f"{quality} version is not available or download failed."}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/download/audio")
async def download_audio_endpoint(url: str = Query(...)):
    try:
        file_path = download_youtube_audio(url)
        if file_path and os.path.exists(file_path):
            return FileResponse(file_path, filename=os.path.basename(file_path), media_type='application/octet-stream')
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

