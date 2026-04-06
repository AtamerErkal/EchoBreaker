import yt_dlp
from typing import Tuple
from models.analysis_result import VideoMetadata


class YouTubeExtractor:
    """Extracts metadata + captions from YouTube. No audio download needed."""

    def _format_duration(self, seconds: int) -> str:
        if not seconds:
            return "00:00"
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{h:d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

    def _format_views(self, views: int) -> str:
        if not views:
            return "0"
        if views >= 1_000_000:
            return f"{views / 1_000_000:.1f}M"
        elif views >= 1_000:
            return f"{views / 1_000:.1f}K"
        return str(views)

    def _format_date(self, date_str: str) -> str:
        if not date_str or len(date_str) != 8:
            return date_str or "Unknown"
        return f"{date_str[6:8]}.{date_str[4:6]}.{date_str[0:4]}"

    def extract(self, url: str) -> Tuple[str, VideoMetadata]:
        """
        Extracts captions + metadata. Returns (transcript, VideoMetadata).
        Uses auto-generated captions — no audio download, no transcription needed.
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'writeautomaticsub': True,
            'writesubtitles': True,
            'subtitleslangs': ['en', 'en-US', 'en-GB', 'de', 'tr'],
            'subtitlesformat': 'json3',
            'ignoreerrors': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise Exception("Could not extract video information")

            # --- Extract transcript from captions ---
            transcript = self._get_transcript(info)

            # --- Build metadata ---
            duration_raw = info.get('duration', 0)
            views_raw = info.get('view_count', 0)

            metadata = VideoMetadata(
                video_title=info.get('title', 'Unknown Title'),
                channel_name=info.get('uploader') or info.get('channel', 'Unknown'),
                duration=self._format_duration(duration_raw),
                duration_seconds=duration_raw,
                view_count=self._format_views(views_raw),
                view_count_raw=views_raw,
                upload_date=self._format_date(info.get('upload_date', '')),
                thumbnail=info.get('thumbnail'),
                description=info.get('description', '')[:500] if info.get('description') else None,
            )

            return transcript, metadata

    def _get_transcript(self, info: dict) -> str:
        """Extract transcript from subtitles or auto-captions."""
        # Try manual subtitles first, then auto-generated
        for sub_source in [info.get('subtitles', {}), info.get('automatic_captions', {})]:
            for lang in ['en', 'en-US', 'en-GB', 'de', 'tr']:
                if lang in sub_source:
                    formats = sub_source[lang]
                    # Prefer json3, then vtt, then any
                    for fmt in formats:
                        if fmt.get('ext') == 'json3' and fmt.get('url'):
                            return self._fetch_json3_transcript(fmt['url'])
                        elif fmt.get('ext') == 'vtt' and fmt.get('url'):
                            return self._fetch_vtt_transcript(fmt['url'])

        # Fallback: use video description as context
        desc = info.get('description', '')
        if desc and len(desc) > 100:
            return f"[Video description used as context] {desc}"

        raise Exception("No captions or subtitles available for this video")

    def _fetch_json3_transcript(self, url: str) -> str:
        """Fetch and parse json3 subtitle format."""
        import requests
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        segments = []
        for event in data.get('events', []):
            segs = event.get('segs', [])
            text = ''.join(s.get('utf8', '') for s in segs).strip()
            if text and text != '\n':
                segments.append(text)

        return ' '.join(segments)

    def _fetch_vtt_transcript(self, url: str) -> str:
        """Fetch and parse VTT subtitle format."""
        import re
        import requests
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()

        lines = resp.text.split('\n')
        text_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('WEBVTT') or '-->' in line or line.isdigit():
                continue
            clean = re.sub(r'<[^>]+>', '', line)
            if clean:
                text_lines.append(clean)

        # Deduplicate consecutive identical lines (VTT repeats)
        deduped = []
        for line in text_lines:
            if not deduped or line != deduped[-1]:
                deduped.append(line)

        return ' '.join(deduped)
