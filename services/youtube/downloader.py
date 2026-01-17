import os
import yt_dlp
from core.config import Config

class YouTubeDownloader:
    def __init__(self, output_dir: str = "temp_audio"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def download_audio(self, url: str) -> str:
        """
        Downloads audio from a YouTube URL, converting it to 16kHz Mono WAV.
        Truncates to the first 300 seconds.
        Returns the absolute path to the downloaded file.
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_dir, '%(id)s.%(ext)s'),
            'ffmpeg_location': '.',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'postprocessor_args': [
                '-ac', '1',          # Mono
                '-ar', '16000',      # 16kHz
                '-t', '300'          # Truncate to 300 seconds
            ],
            'quiet': True,
            'overwrites': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # processing creates a .wav file, we need to return that
                base, _ = os.path.splitext(filename)
                final_path = base + ".wav"
                
                if not os.path.exists(final_path):
                    raise FileNotFoundError(f"Expected output file not found: {final_path}")
                
                return os.path.abspath(final_path)

        except Exception as e:
            # Re-raise or log error
            print(f"Error downloading video: {e}")
            raise e
