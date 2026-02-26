import os
import yt_dlp
from typing import Tuple, Optional
from yt_dlp.utils import download_range_func
from models.analysis_result import VideoMetadata

class YouTubeDownloader:
    def __init__(self, output_dir: str = "temp_audio"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _get_ffmpeg_path(self):
        """Locates ffmpeg executable in the project root."""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            ffmpeg_path = os.path.join(project_root, 'ffmpeg.exe') 
            if os.path.exists(ffmpeg_path):
                return project_root
            return None
        except:
            return None

    def _format_duration(self, seconds: int) -> str:
        """Format duration as HH:MM:SS or MM:SS."""
        if not seconds: 
            return "00:00"
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def _format_views(self, views: int) -> str:
        """Format view count as 1.5M, 250K, etc."""
        if not views: 
            return "0"
        if views >= 1_000_000:
            return f"{views/1_000_000:.1f}M"
        elif views >= 1_000:
            return f"{views/1_000:.1f}K"
        return str(views)

    def _format_date(self, date_str: str) -> str:
        """Format YYYYMMDD to DD.MM.YYYY."""
        if not date_str or len(date_str) != 8:
            return date_str or "Unknown"
        return f"{date_str[6:8]}.{date_str[4:6]}.{date_str[0:4]}"

    def download_audio_with_metadata(self, url: str) -> Tuple[str, Optional[VideoMetadata]]:
        """
        Downloads audio and returns (file_path, VideoMetadata).
        Compatible with main.py expectations.
        """
        ffmpeg_location = self._get_ffmpeg_path()
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_dir, '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            # Limit to first 5 minutes for speed
            'download_ranges': download_range_func(None, [(0, 300)]),
            'force_keyframes_at_cuts': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav', 
                'preferredquality': '192',
            }],
        }

        if ffmpeg_location:
            ydl_opts['ffmpeg_location'] = ffmpeg_location

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if not info:
                    raise Exception("Could not extract video information")
                
                video_id = info.get('id')
                final_path = os.path.abspath(os.path.join(self.output_dir, f"{video_id}.wav"))
                
                if not os.path.exists(final_path):
                    raise FileNotFoundError(f"Audio file not created: {final_path}")

                # Get raw values
                duration_raw = info.get('duration', 0)
                views_raw = info.get('view_count', 0)

                # Create VideoMetadata with BOTH formatted and raw values
                metadata = VideoMetadata(
                    video_title=info.get('title', 'Unknown Title'),
                    channel_name=info.get('uploader') or info.get('channel', 'Unknown'),
                    duration=self._format_duration(duration_raw),
                    duration_seconds=duration_raw,  # NEW: Raw seconds
                    view_count=self._format_views(views_raw),
                    view_count_raw=views_raw,  # NEW: Raw integer
                    upload_date=self._format_date(info.get('upload_date', '')),
                    thumbnail=info.get('thumbnail'),
                    description=info.get('description', '')[:500] if info.get('description') else None
                )

                print(f"✅ Downloaded: {metadata.video_title}")
                return final_path, metadata

        except Exception as e:
            print(f"❌ Download Error: {str(e)}")
            raise e