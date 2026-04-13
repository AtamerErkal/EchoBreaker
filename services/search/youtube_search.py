import asyncio
import logging
import yt_dlp
from typing import List
from concurrent.futures import ThreadPoolExecutor
from models.analysis_result import VideoSuggestion

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=3)

    def _is_quality_title(self, title: str) -> bool:
        if not title:
            return False
        clickbait_terms = ['SHOCKING', "YOU WON'T BELIEVE", 'MUST WATCH', 'GONE WRONG']
        title_upper = title.upper()
        for term in clickbait_terms:
            if term in title_upper:
                return False
        emoji_count = sum(1 for c in title if ord(c) > 0x1F300)
        if emoji_count > 3:
            return False
        caps_ratio = sum(1 for c in title if c.isupper()) / max(len(title), 1)
        if caps_ratio > 0.7 and len(title) > 10:
            return False
        return True

    def _safe_int(self, value, default=0) -> int:
        if value is None:
            return default
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value.replace(',', ''))
            except Exception:
                return default
        return default

    async def search_videos(self, query: str, limit: int = 3) -> List[VideoSuggestion]:
        query = query.strip("'\"\\ ")

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'noplaylist': True,
            'skip_download': True,
            'extract_flat': 'in_playlist',
            'ignoreerrors': True,
        }

        loop = asyncio.get_running_loop()

        def _search():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_query = f"ytsearch{limit + 2}:{query}"
                try:
                    result = ydl.extract_info(search_query, download=False)
                    return result.get('entries', []) if result else []
                except Exception as e:
                    logger.error("Search error: %s", e, exc_info=True)
                    return []

        try:
            entries = await loop.run_in_executor(self._executor, _search)

            results = []
            for entry in entries:
                if not entry:
                    continue

                title = entry.get('title')
                url = entry.get('url') or entry.get('webpage_url')
                if not title or not url:
                    continue

                if not url.startswith('http'):
                    url = f"https://www.youtube.com/watch?v={url}"

                if not self._is_quality_title(title):
                    continue

                video = VideoSuggestion(
                    title=title,
                    url=url,
                    thumbnail=entry.get('thumbnail'),
                    duration=entry.get('duration'),
                    channel_name=entry.get('uploader') or entry.get('channel'),
                    view_count=self._safe_int(entry.get('view_count')),
                    description=entry.get('description', '')[:300] if entry.get('description') else '',
                    relevance_score=0.75,
                )
                results.append(video)
                if len(results) >= limit:
                    break

            return results

        except Exception as e:
            logger.error("Search exception for '%s': %s", query, e, exc_info=True)
            return []
