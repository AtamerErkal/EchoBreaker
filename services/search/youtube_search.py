import asyncio
import yt_dlp
from typing import List
from concurrent.futures import ThreadPoolExecutor
from models.analysis_result import VideoSuggestion

class SearchService:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=2)
        
    async def search_videos(self, query: str, limit: int = 2) -> List[VideoSuggestion]:
        """
        Searches YouTube using the native yt_dlp Python class in a thread pool.
        """
        # Ensure query is clean
        query = query.strip('"\' ')
        
        ydl_opts = {
            'quiet': True,
            'default_search': 'ytsearch',
            'noplaylist': True,
            'extract_flat': True, # We only need metadata, not download
        }

        loop = asyncio.get_running_loop()

        def _search():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # ytsearchN:query returns a dictionary with 'entries'
                search_query = f"ytsearch{limit}:{query}"
                result = ydl.extract_info(search_query, download=False)
                return result.get('entries', [])

        try:
            print(f"DEBUG: Searching YT for keywords: {query}")
            entries = await loop.run_in_executor(self._executor, _search)
            
            results = []
            for entry in entries:
                results.append(VideoSuggestion(
                    title=entry.get('title', 'Unknown Title'),
                    url=entry.get('url') or entry.get('webpage_url', ''),
                    thumbnail=entry.get('thumbnail')
                ))
            
            return results

        except Exception as e:
            print(f"Exception during YouTube search for '{query}': {e}")
            return []
