import asyncio
import yt_dlp
from typing import List
from concurrent.futures import ThreadPoolExecutor
from models.analysis_result import VideoSuggestion

class SearchService:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=2)
    
    def _is_quality_title(self, title: str) -> bool:
        """Check if video title meets quality standards (not clickbait)."""
        if not title:
            return False
        
        # Reject clickbait indicators
        clickbait_terms = ['SHOCKING', 'YOU WON\'T BELIEVE', 'MUST WATCH', 'GONE WRONG']
        title_upper = title.upper()
        
        for term in clickbait_terms:
            if term in title_upper:
                return False
        
        # Reject excessive emoji or all caps
        emoji_count = sum(1 for c in title if ord(c) > 0x1F300)
        if emoji_count > 3:
            return False
        
        caps_ratio = sum(1 for c in title if c.isupper()) / max(len(title), 1)
        if caps_ratio > 0.7 and len(title) > 10:  # More than 70% caps
            return False
        
        return True
    
    def _calculate_authority_score(self, entry: dict) -> float:
        """Calculate source authority score based on category and metadata."""
        score = 0.5  # Base score
        
        # Boost for educational categories
        categories = entry.get('categories', [])
        if categories:
            if any(cat in ['News', 'Education', 'Documentary', 'Science & Technology'] for cat in categories):
                score += 0.3
        
        # Boost for certain channel indicators
        uploader = (entry.get('uploader') or entry.get('channel') or '').lower()
        if any(term in uploader for term in ['university', 'institute', 'news', 'academy', 'research']):
            score += 0.2
        
        return min(score, 1.0)
        
    async def search_videos(self, query: str, limit: int = 5) -> List[VideoSuggestion]:
        """
        Searches YouTube using the native yt_dlp Python class in a thread pool.
        Extracts comprehensive metadata and filters for quality.
        """
        # Ensure query is clean
        query = query.strip("'\"\\ ")
        
        ydl_opts = {
            'quiet': True,
            'default_search': 'ytsearch',
            'noplaylist': True,
            'skip_download': True,  # Don't download, just extract metadata
            'format': 'bestaudio/best',
            'extract_flat': False,  # Get full metadata
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
            }
        }

        loop = asyncio.get_running_loop()

        def _search():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # ytsearchN:query returns a dictionary with 'entries'
                # Request more than needed to account for filtering
                search_query = f"ytsearch{limit * 2}:{query}"
                result = ydl.extract_info(search_query, download=False)
                return result.get('entries', [])

        try:
            print(f"DEBUG: Searching YT for keywords: {query}")
            entries = await loop.run_in_executor(self._executor, _search)
            
            results = []
            for entry in entries:
                if not entry:
                    continue
                
                title = entry.get('title', 'Unknown Title')
                
                # Apply quality filter
                if not self._is_quality_title(title):
                    print(f"DEBUG: Rejected low-quality title: {title}")
                    continue
                
                # Extract metadata
                duration = entry.get('duration')  # In seconds
                channel_name = entry.get('uploader') or entry.get('channel')
                view_count = entry.get('view_count', 0)
                description = entry.get('description', '')[:500]  # Limit to 500 chars
                
                # Calculate base authority score (will be updated by relevance check)
                authority = self._calculate_authority_score(entry)
                
                results.append(VideoSuggestion(
                    title=title,
                    url=entry.get('url') or entry.get('webpage_url', ''),
                    thumbnail=entry.get('thumbnail'),
                    duration=duration,
                    channel_name=channel_name,
                    view_count=view_count,
                    description=description,
                    relevance_score=authority  # Initial score, will be refined by verification
                ))
                
                # Stop once we have enough quality results
                if len(results) >= limit:
                    break
            
            print(f"DEBUG: Found {len(results)} quality videos after filtering")
            return results

        except Exception as e:
            print(f"Exception during YouTube search for '{query}': {e}")
            return []
