import os
import whisper
import asyncio
from concurrent.futures import ThreadPoolExecutor

class TranscriptionService:
    def __init__(self):
        # Load the model once at initialization
        # Use CUDA if available, otherwise fallback to CPU
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading Whisper model (tiny) on {device}...")
        self.model = whisper.load_model("tiny", device=device)
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def transcribe_file(self, audio_file_path: str) -> str:
        """
        Transcribes an audio file locally using Whisper.
        Runs the blocking Whisper call in a separate thread to avoid blocking the asyncio loop.
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        loop = asyncio.get_running_loop()
        
        # Whisper transcribe is blocking, run in executor
        result = await loop.run_in_executor(
            self._executor, 
            self.model.transcribe, 
            audio_file_path
        )
        
        return result["text"]
