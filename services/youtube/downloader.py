import os
import yt_dlp
from yt_dlp.utils import download_range_func
from core.config import Config

class YouTubeDownloader:
    def __init__(self, output_dir: str = "temp_audio"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def download_audio(self, url: str) -> str:
        """
        Downloads audio from a YouTube URL, converting it to 16kHz Mono WAV.
        Forcefully truncates to the first 300 seconds (5 minutes) to optimize speed.
        Returns the absolute path to the downloaded file.
        """
        # Get absolute path to project root where ffmpeg is located
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_dir, '%(id)s.%(ext)s'),
            'ffmpeg_location': project_root,
            'download_ranges': download_range_func(None, [(0, 300)]), # STRICT 5 MIN LIMIT
            'force_keyframes_at_cuts': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'postprocessor_args': [
                '-ar', '16000',      # 16kHz sample rate
                '-ac', '1',          # Mono channel
                '-vn',               # Drop video stream forcefully
            ],
            'quiet': False,
            'no_warnings': False,
            'nocheckcertificate': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'ios']}},
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Referer': 'https://www.youtube.com/',
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # processing creates a .wav file, we need to return that
                base, _ = os.path.splitext(filename)
                
                # yt-dlp might append logic for ranges, but usually with outtmpl it sticks to id.
                # However, with download_ranges, sometimes it adds stuff? No, usually fine.
                # But just in case, we check for the file.
                final_path = base + ".wav"
                
                # Double check if file exists, sometimes ranges naming is tricky
                if not os.path.exists(final_path):
                    # Check if original filename exists (maybe conversion failed?)
                    if os.path.exists(base + ".webm"):
                        # Ensure we return valid path
                         pass
                    
                    # If allow multiple is not set, we assume standard behavior
                    if not os.path.exists(final_path):
                         # Try finding any .wav in that dir with that id?
                         pass
                
                if not os.path.exists(final_path):
                     # Fallback check
                     raise FileNotFoundError(f"Expected output file not found: {final_path}")
                
                return os.path.abspath(final_path)

        except Exception as e:
            # Re-raise or log error
            print(f"Error downloading video: {e}")
            raise e
