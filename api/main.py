import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List

from core.config import Config
from models.analysis_result import AnalysisResult, VideoSuggestion
from services.youtube.downloader import YouTubeExtractor
from services.reasoning.generator import create_reasoning_engine
from services.search.youtube_search import SearchService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="EchoBreaker API", version="5.1.0")

# Initialize Services
extractor = YouTubeExtractor()
searcher = SearchService()
try:
    logger.info("Initializing EchoBreaker (provider: %s)...", Config.PROVIDER)
    reasoner = create_reasoning_engine()
    logger.info("Ready.")
except Exception as e:
    logger.error("Failed to initialize reasoning engine: %s", e, exc_info=True)
    reasoner = None


class AnalyzeRequest(BaseModel):
    video_url: str
    language: str = "en"


class SearchSourcesRequest(BaseModel):
    youtube_query: str


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_video(request: AnalyzeRequest):
    """
    Fast pipeline (~5 seconds):
    1. Extract captions + metadata (yt-dlp, no download)
    2. Analyze with LLM (Azure OpenAI or Groq)
    """
    if reasoner is None:
        raise HTTPException(
            status_code=503,
            detail="Analysis engine not initialized. Check your .env configuration (AZURE_OPENAI_API_KEY or GROQ_API_KEY)."
        )
    
    try:
        logger.info("[1/2] Extracting: %s", request.video_url)
        transcript, metadata = extractor.extract(request.video_url)

        logger.info("[2/2] Analyzing (%d chars)...", len(transcript))
        result = reasoner.generate_analysis(transcript, request.video_url, language=request.language)
        result.video_metadata = metadata

        logger.info("Done.")
        return result

    except Exception as e:
        logger.error("Pipeline error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search-sources", response_model=List[VideoSuggestion])
async def search_sources(request: SearchSourcesRequest):
    """Lazy source loading - called when user clicks 'Explore Sources'."""
    try:
        results = await searcher.search_videos(request.youtube_query, limit=3)
        return results
    except Exception as e:
        logger.error("Search error: %s", e, exc_info=True)
        return []


@app.get("/api/health")
def health_check():
    return {
        "status": "operational",
        "version": "5.1.0",
        "provider": Config.PROVIDER,
    }


# Serve frontend
ROOT_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
IMAGES_DIR   = os.path.join(ROOT_DIR, "images")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index_v6.html"))

# Static files - mount AFTER specific routes
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
