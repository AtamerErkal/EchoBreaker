from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
from core.config import Config
from models.analysis_result import AnalysisResult
from services.youtube.downloader import YouTubeDownloader
from services.audio.transcription import create_transcription_service
from services.reasoning.generator import create_reasoning_engine
from services.search.youtube_search import SearchService

app = FastAPI(title="EchoBreaker API", version="3.0.0")

# Initialize Services
try:
    print(f"Initializing EchoBreaker Services (provider: {Config.PROVIDER})...")
    yt_downloader = YouTubeDownloader()
    transcriber = create_transcription_service()
    reasoner = create_reasoning_engine()
    searcher = SearchService()
    print("Services initialized.")
except Exception as e:
    print(f"Failed to initialize services: {e}")

class AnalyzeRequest(BaseModel):
    video_url: str

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_video(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    EchoBreaker pipeline:
    1. Download Audio + Extract Metadata (yt-dlp)
    2. Transcribe (Azure Speech or Whisper)
    3. Analyze & Generate Counter-Arguments (Azure OpenAI or Ollama)
    4. Search & Verify Counter-Sources (yt-dlp + dual-pass)
    """
    temp_file = None
    try:
        # 1. Download + Extract Metadata
        print(f"[1/4] Downloading: {request.video_url}")
        temp_file, video_metadata = yt_downloader.download_audio_with_metadata(request.video_url)

        # 2. Transcribe
        print("[2/4] Transcribing...")
        transcript = await transcriber.transcribe_file(temp_file)
        if not transcript:
            raise HTTPException(status_code=400, detail="Could not transcribe audio.")

        # 3. Analyze
        print("[3/4] Analyzing arguments...")
        result = reasoner.generate_analysis(transcript, request.video_url)
        result.video_metadata = video_metadata

        # 4. Search + Verify
        print("[4/4] Searching for counter-sources...")
        import asyncio

        async def process_counter_argument(argument):
            if not argument.youtube_query:
                return
            try:
                suggestions = await searcher.search_videos(argument.youtube_query, limit=3)
                verified = []
                for video in suggestions:
                    verification = reasoner.verify_relevance(
                        counter_argument_content=argument.content,
                        video_title=video.title,
                        video_description=video.description or "",
                    )
                    score = verification.get("score", 0.5)
                    if verification.get("verdict") == "accept" and score >= 0.7:
                        video.relevance_score = score
                        verified.append(video)

                verified.sort(key=lambda v: v.relevance_score or 0, reverse=True)
                argument.suggested_videos = verified[:3]
            except Exception as e:
                print(f"  Search failed for '{argument.youtube_query}': {e}")

        await asyncio.gather(*(process_counter_argument(arg) for arg in result.counter_arguments))

        print("Pipeline complete.")
        return result

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Pipeline error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass

@app.get("/")
def health_check():
    return {
        "status": "EchoBreaker API is operational",
        "version": "3.0.0",
        "provider": Config.PROVIDER,
    }
