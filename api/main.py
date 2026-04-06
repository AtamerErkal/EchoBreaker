from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import os
from core.config import Config
from models.analysis_result import AnalysisResult, VideoSuggestion
from services.youtube.downloader import YouTubeExtractor
from services.reasoning.generator import create_reasoning_engine
from services.search.youtube_search import SearchService

app = FastAPI(title="EchoBreaker API", version="5.0.0")

# Initialize Services
try:
    print(f"Initializing EchoBreaker (provider: {Config.PROVIDER})...")
    extractor = YouTubeExtractor()
    reasoner = create_reasoning_engine()
    searcher = SearchService()
    print("Ready.")
except Exception as e:
    print(f"Failed to initialize: {e}")


class AnalyzeRequest(BaseModel):
    video_url: str


class SearchSourcesRequest(BaseModel):
    youtube_query: str


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_video(request: AnalyzeRequest):
    """
    Fast pipeline (~5 seconds):
    1. Extract captions + metadata (yt-dlp, no download)
    2. Analyze with LLM (Azure OpenAI or Ollama)
    """
    try:
        print(f"[1/2] Extracting: {request.video_url}")
        transcript, metadata = extractor.extract(request.video_url)

        print(f"[2/2] Analyzing ({len(transcript)} chars)...")
        result = reasoner.generate_analysis(transcript, request.video_url)
        result.video_metadata = metadata

        print("Done.")
        return result

    except Exception as e:
        import traceback
        print(f"Pipeline error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search-sources", response_model=List[VideoSuggestion])
async def search_sources(request: SearchSourcesRequest):
    """Lazy source loading - called when user clicks 'Explore Sources'."""
    try:
        results = await searcher.search_videos(request.youtube_query, limit=3)
        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []


@app.get("/api/health")
def health_check():
    return {
        "status": "operational",
        "version": "5.0.0",
        "provider": Config.PROVIDER,
    }


# Serve frontend
ROOT_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
IMAGES_DIR   = os.path.join(ROOT_DIR, "images")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index_v3.html"))

# Static files - mount AFTER specific routes
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
