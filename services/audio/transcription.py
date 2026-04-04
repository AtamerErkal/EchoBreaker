import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from core.config import Config


class AzureTranscriptionService:
    """Uses Azure Speech Services for fast cloud-based transcription."""

    def __init__(self):
        import azure.cognitiveservices.speech as speechsdk
        self.speechsdk = speechsdk
        self.speech_config = speechsdk.SpeechConfig(
            subscription=Config.AZURE_SPEECH_KEY,
            region=Config.AZURE_SPEECH_REGION,
        )
        self.speech_config.speech_recognition_language = "en-US"

    async def transcribe_file(self, audio_file_path: str) -> str:
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._transcribe_sync, audio_file_path)

    def _transcribe_sync(self, audio_file_path: str) -> str:
        audio_config = self.speechsdk.AudioConfig(filename=audio_file_path)
        recognizer = self.speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config,
        )

        all_text = []
        done = asyncio.Event.__class__()  # threading.Event equivalent

        import threading
        done_event = threading.Event()

        def on_recognized(evt):
            if evt.result.reason == self.speechsdk.ResultReason.RecognizedSpeech:
                all_text.append(evt.result.text)

        def on_canceled(evt):
            done_event.set()

        def on_stopped(evt):
            done_event.set()

        recognizer.recognized.connect(on_recognized)
        recognizer.canceled.connect(on_canceled)
        recognizer.session_stopped.connect(on_stopped)

        recognizer.start_continuous_recognition()
        done_event.wait(timeout=600)  # 10 min max
        recognizer.stop_continuous_recognition()

        return " ".join(all_text)


class WhisperTranscriptionService:
    """Uses local Whisper for fully private, offline transcription."""

    def __init__(self):
        import torch
        import whisper
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"  Loading Whisper model (tiny) on {device}...")
        self.model = whisper.load_model("tiny", device=device)
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def transcribe_file(self, audio_file_path: str) -> str:
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self._executor,
            self.model.transcribe,
            audio_file_path,
        )
        return result["text"]


def create_transcription_service():
    if Config.PROVIDER == "azure" and Config.AZURE_SPEECH_KEY:
        print("  Using Azure Speech for transcription")
        return AzureTranscriptionService()
    else:
        print("  Using Whisper (local) for transcription")
        return WhisperTranscriptionService()
