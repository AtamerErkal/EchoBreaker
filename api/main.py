from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
import shutil
from core.config import Config
from models.analysis_result import AnalysisResult
from services.youtube.downloader import YouTubeDownloader
from services.audio.transcription import TranscriptionService
from services.reasoning.generator import ReasoningEngine
from services.search.youtube_search import SearchService

app = FastAPI(title="EchoBreaker API (Local)", version="2.1.0")

# Initialize Services
try:
    print("Initializing EchoBreaker Local Services...")
    yt_downloader = YouTubeDownloader()
    transcriber = TranscriptionService() # Loads Whisper model
    reasoner = ReasoningEngine()         # Connects to Ollama
    searchER = SearchService()
    print("Services Initialized.")
except Exception as e:
    print(f"Failed to initialize services: {e}")

class AnalyzeRequest(BaseModel):
    video_url: str

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_video(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Orchestrates the Local EchoBreaker pipeline:
    1. Download Audio (yt-dlp)
    2. Transcribe (Whisper Local)
    3. Intelligence (Ollama / Llama 3) - Combined Analysis & Reasoning
    4. Search (yt-dlp) - Find video suggestions for counter-arguments
    """
    temp_file = None
    try:
        # 1. Download
        print(f"Downloading: {request.video_url}")
        temp_file = yt_downloader.download_audio(request.video_url)
        
        # 2. Transcribe
        print("Transcribing with Whisper...")
        transcript = await transcriber.transcribe_file(temp_file)
        if not transcript:
            raise HTTPException(status_code=400, detail="Could not transcribe audio.")

        # 3. Intelligence (Combined Analysis & Reasoning)
        print("Running Llama 3 Analysis...")
        result = reasoner.generate_analysis(transcript, request.video_url)
        
        # 4. Search for Counter-Argument Videos with Dual-Pass Verification
        print("Searching for suggested videos with relevance verification...")
        if not searchER:
             print("Warning: SearchService not initialized")
        else:
            for argument in result.counter_arguments:
                if argument.youtube_query:
                    print(f"Searching for: {argument.youtube_query}")
                    try:
                        # Search for more videos than needed (will filter by relevance)
                        suggestions = await searchER.search_videos(argument.youtube_query, limit=5)
                        print(f"Found {len(suggestions)} videos for query '{argument.youtube_query}'")
                        
                        # Dual-Pass Verification: Check relevance of each video
                        verified_videos = []
                        for video in suggestions:
                            print(f"  Verifying: {video.title[:60]}...")
                            
                            verification = reasoner.verify_relevance(
                                counter_argument_content=argument.content,
                                video_title=video.title,
                                video_description=video.description or ""
                            )
                            
                            relevance_score = verification.get('score', 0.5)
                            verdict = verification.get('verdict', 'reject')
                            reason = verification.get('reason', '')
                            
                            print(f"    Score: {relevance_score:.2f} | Verdict: {verdict} | {reason}")
                            
                            # Only accept videos with score >= 0.7
                            if verdict == 'accept' and relevance_score >= 0.7:
                                video.relevance_score = relevance_score
                                verified_videos.append(video)
                            else:
                                print(f"    ❌ Rejected: Low relevance")
                        
                        # Keep top 2 verified videos
                        verified_videos.sort(key=lambda v: v.relevance_score or 0, reverse=True)
                        argument.suggested_videos = verified_videos[:2]
                        
                        print(f"  ✅ Accepted {len(argument.suggested_videos)} videos after verification")
                        
                    except Exception as sx:
                        print(f"Search/verification failed for {argument.youtube_query}: {sx}")
                        import traceback
                        traceback.print_exc()
        
        
        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temp file
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                print(f"Error cleaning up file {temp_file}")

@app.get("/")
def health_check():
    return {"status": "EchoBreaker (Local) is operational"}
