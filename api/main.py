from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
import asyncio
import traceback
from core.config import Config
from models.analysis_result import AnalysisResult, VideoMetadata
from services.youtube.downloader import YouTubeDownloader
from services.audio.transcription import TranscriptionService
from services.reasoning.generator import ReasoningEngine
from services.search.youtube_search import SearchService

app = FastAPI(title="EchoBreaker API", version="2.2.0")

# =============================================================================
# SERVICE INITIALIZATION
# =============================================================================
try:
    print("🚀 Initializing EchoBreaker Local Services...")
    yt_downloader = YouTubeDownloader()
    transcriber = TranscriptionService() # Loads local Whisper model
    reasoner = ReasoningEngine()         # Connects to local Ollama/Llama 3
    search_service = SearchService()     # YouTube search integration
    print("✅ All services initialized successfully.")
except Exception as e:
    print(f"❌ Critical Error during service initialization: {e}")
    traceback.print_exc()

class AnalyzeRequest(BaseModel):
    video_url: str

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_video(request: AnalyzeRequest):
    """
    Orchestrates the full EchoBreaker pipeline:
    1. Download audio and extract metadata via yt-dlp.
    2. Transcribe audio locally using Whisper.
    3. Analyze topic, claims, and generate counter-perspectives using Llama 3.
    4. Search YouTube for videos matching those counter-perspectives.
    5. Verify video relevance using AI fallback logic.
    """
    temp_file = None
    try:
        # STEP 1: DOWNLOAD & METADATA
        print(f"\n--- [Step 1] Processing Video: {request.video_url} ---")
        # Returns (absolute_path, metadata_dictionary)
        temp_file, meta_dict = yt_downloader.download_audio_with_metadata(request.video_url)
        
        # STEP 2: TRANSCRIPTION
        print("--- [Step 2] Transcribing with Local Whisper ---")
        transcript = await transcriber.transcribe_file(temp_file)
        if not transcript:
            raise HTTPException(status_code=400, detail="Transcription failed. Audio might be silent.")

        # STEP 3: REASONING & ANALYSIS
        print("--- [Step 3] Generating Insights with Llama 3 ---")
        # Result contains topic, primary_claim, and counter_arguments list
        result = reasoner.generate_analysis(transcript, request.video_url)
        
        # Inject metadata for the Frontend UI
        result.video_metadata = VideoMetadata(
            video_title=meta_dict.get('title', 'Unknown Title'),
            channel_name=meta_dict.get('channel', 'Unknown Channel'),
            duration=meta_dict.get('duration_formatted', '00:00'),
            view_count=str(meta_dict.get('view_count', '0')),
            upload_date=meta_dict.get('upload_date', 'Unknown'),
            thumbnail=meta_dict.get('thumbnail'),
            description=meta_dict.get('description', '')[:500] # Limit desc length
        )
        
        # STEP 4: SEARCH & VERIFICATION
        print("--- [Step 4] Searching for Diverse Perspectives ---")
        
        async def process_counter_argument(argument):
            query = argument.youtube_query
            if not query:
                return

            try:
                print(f"  🔍 Searching for '{argument.type}': {query}")
                # Get raw search results
                raw_suggestions = await search_service.search_videos(query, limit=3)
                
                verified_videos = []
                for video in raw_suggestions:
                    # AI-powered Relevance Check
                    verification = reasoner.verify_relevance(
                        counter_argument_content=argument.content,
                        video_title=video.title,
                        video_description=video.description or ""
                    )
                    
                    score = verification.get('score', 0.5)
                    verdict = verification.get('verdict', 'reject')
                    
                    # LOGIC: Accept if AI says "accept" OR if score is high enough (>=0.6)
                    if verdict == 'accept' or score >= 0.6:
                        video.relevance_score = score
                        verified_videos.append(video)
                
                # FALLBACK MECHANISM:
                # If the AI was too strict and rejected everything, but we found videos,
                # we keep the #1 search result so the UI isn't empty.
                if not verified_videos and raw_suggestions:
                    print(f"    ⚠️ [Fallback] AI was too strict for '{argument.type}'. Adding top search result.")
                    fallback = raw_suggestions[0]
                    fallback.relevance_score = 0.5 # Default neutral score
                    verified_videos.append(fallback)

                # Final sorting and assignment
                verified_videos.sort(key=lambda v: v.relevance_score or 0, reverse=True)
                argument.suggested_videos = verified_videos[:2] # Return top 2 videos
                print(f"    ✅ Found {len(argument.suggested_videos)} video(s) for {argument.type}")

            except Exception as sx:
                print(f"  ❌ Search task failed: {sx}")

        # Run all category searches (Ethical, Empirical, Logical) concurrently
        if result.counter_arguments:
            await asyncio.gather(*(process_counter_argument(arg) for arg in result.counter_arguments))
        
        print("--- [Final] Pipeline Complete. Returning results. ---\n")
        return result

    except Exception as e:
        print(f"🔥 PIPELINE CRASH: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
    finally:
        # Cleanup temporary audio files
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                print(f"🧹 Cleanup: Removed temporary file {os.path.basename(temp_file)}")
            except Exception as cleanup_err:
                print(f"⚠️ Cleanup failed: {cleanup_err}")

@app.get("/")
def health_check():
    """Returns the current status and configuration of the API."""
    return {
        "status": "online",
        "service": "EchoBreaker API",
        "version": "2.2.0",
        "llm_model": Config.OLLAMA_MODEL
    }