from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
from models.analysis_result import AnalysisResult
from services.youtube.downloader import YouTubeDownloader
from services.audio.transcription import TranscriptionService
from services.reasoning.generator import ReasoningEngine
from services.search.youtube_search import SearchService

app = FastAPI(title="EchoBreaker API", version="2.2.0")

# Initialize Services
try:
    print("🚀 Initializing EchoBreaker Services...")
    yt_downloader = YouTubeDownloader()
    transcriber = TranscriptionService()
    reasoner = ReasoningEngine()
    searchER = SearchService()
    print("✅ Services Initialized.")
except Exception as e:
    print(f"❌ Failed to initialize services: {e}")

class AnalyzeRequest(BaseModel):
    video_url: str

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_video(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Orchestrates the EchoBreaker pipeline:
    1. Download Audio + Extract Metadata (yt-dlp)
    2. Transcribe (Whisper Local)
    3. Intelligence (Ollama / Llama 3)
    4. Search & Verify (yt-dlp + dual-pass)
    """
    temp_file = None
    try:
        # 1. Download + Extract Metadata
        print(f"📥 Downloading: {request.video_url}")
        temp_file, video_metadata = yt_downloader.download_audio_with_metadata(request.video_url)
        
        # 2. Transcribe
        print("🎤 Transcribing with Whisper...")
        transcript = await transcriber.transcribe_file(temp_file)
        if not transcript:
            raise HTTPException(status_code=400, detail="Could not transcribe audio.")

        # 3. Intelligence (Analysis + Reasoning)
        print("🧠 Running Llama 3 Analysis...")
        result = reasoner.generate_analysis(transcript, request.video_url)
        
        # CRITICAL FIX: VideoMetadata is already a Pydantic object, not a dict
        # Just assign it directly
        result.video_metadata = video_metadata
        
        # 4. Search for Counter-Argument Videos (Parallel)
        print("🔍 Searching for verified sources (parallel)...")
        if searchER:
            import asyncio

            async def process_counter_argument(argument):
                if not argument.youtube_query:
                    print(f"  ⚠️ No search query for {argument.type}")
                    return

                try:
                    print(f"  🔎 Searching: {argument.youtube_query}")
                    suggestions = await searchER.search_videos(argument.youtube_query, limit=3)
                    
                    verified_videos = []
                    for video in suggestions:
                        # Verify relevance
                        verification = reasoner.verify_relevance(
                            counter_argument_content=argument.content,
                            video_title=video.title,
                            video_description=video.description or ""
                        )
                        
                        relevance_score = verification.get('score', 0.5)
                        verdict = verification.get('verdict', 'reject')
                        
                        if verdict == 'accept' and relevance_score >= 0.7:
                            video.relevance_score = relevance_score
                            verified_videos.append(video)
                            print(f"    ✅ Verified: {video.title[:50]}... (score: {relevance_score:.2f})")
                        else:
                            print(f"    ❌ Rejected: {video.title[:50]}... (score: {relevance_score:.2f})")
                    
                    # Keep top 3 verified videos
                    verified_videos.sort(key=lambda v: v.relevance_score or 0, reverse=True)
                    argument.suggested_videos = verified_videos[:3]
                    print(f"  ✅ Found {len(argument.suggested_videos)} video(s) for {argument.type}")

                except Exception as sx:
                    print(f"  ❌ Search failed for {argument.youtube_query}: {sx}")

            # Run all searches concurrently
            await asyncio.gather(*(process_counter_argument(arg) for arg in result.counter_arguments))
        else:
            print("⚠️ SearchService not initialized")
        
        print("--- [Final] Pipeline Complete. Returning results. ---")
        return result

    except Exception as e:
        import traceback
        print(f"🔥 PIPELINE CRASH: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temp file
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                print(f"🧹 Cleanup: Removed temporary file {os.path.basename(temp_file)}")
            except Exception as cleanup_error:
                print(f"⚠️ Cleanup error: {cleanup_error}")

@app.get("/")
def health_check():
    return {"status": "EchoBreaker API is operational", "version": "2.2.0"}