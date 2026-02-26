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
        if caps_ratio > 0.7 and len(title) > 10:
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
    
    def _safe_int(self, value, default=0) -> int:
        """Safely convert value to int."""
        if value is None:
            return default
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value.replace(',', ''))
            except:
                return default
        return default
        
    async def search_videos(self, query: str, limit: int = 3) -> List[VideoSuggestion]:
        """
        Searches YouTube using yt_dlp with proper error handling.
        Returns list of VideoSuggestion objects.
        """
        query = query.strip("'\"\\ ")
        
        ydl_opts = {
            'quiet': True,
            'default_search': 'ytsearch',
            'noplaylist': True,
            'skip_download': True,
            'format': 'bestaudio/best',
            'extract_flat': False,
            'ignoreerrors': True,  # CRITICAL: Skip failed videos
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
            }
        }

        loop = asyncio.get_running_loop()

        def _search():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Request more to account for filtering
                search_query = f"ytsearch{limit * 3}:{query}"
                try:
                    result = ydl.extract_info(search_query, download=False)
                    return result.get('entries', []) if result else []
                except Exception as e:
                    print(f"DEBUG: Search extraction error: {e}")
                    return []

        try:
            print(f"DEBUG: Searching YT for: {query}")
            entries = await loop.run_in_executor(self._executor, _search)
            
            results = []
            for entry in entries:
                if not entry:
                    continue
                
                # Get basic info
                title = entry.get('title')
                url = entry.get('url') or entry.get('webpage_url')
                
                # Skip if missing critical data
                if not title or not url:
                    print(f"DEBUG: Skipping entry - missing title or URL")
                    continue
                
                # Apply quality filter
                if not self._is_quality_title(title):
                    print(f"DEBUG: Rejected clickbait: {title[:50]}")
                    continue
                
                # Extract and validate metadata
                try:
                    duration = entry.get('duration')  # Already int or None
                    channel_name = entry.get('uploader') or entry.get('channel')
                    
                    # CRITICAL FIX: Safely convert view_count to int
                    view_count = self._safe_int(entry.get('view_count'), default=0)
                    
                    description = entry.get('description', '')[:500] if entry.get('description') else ''
                    thumbnail = entry.get('thumbnail')
                    authority = self._calculate_authority_score(entry)
                    
                    # Create VideoSuggestion with validated data
                    video = VideoSuggestion(
                        title=title,
                        url=url,
                        thumbnail=thumbnail,
                        duration=duration,
                        channel_name=channel_name,
                        view_count=view_count,  # Now guaranteed int
                        description=description,
                        relevance_score=authority
                    )
                    
                    results.append(video)
                    
                    if len(results) >= limit:
                        break
                        
                except Exception as parse_error:
                    print(f"DEBUG: Error parsing video: {parse_error}")
                    continue
            
            print(f"DEBUG: Found {len(results)} quality videos")
            return results

        except Exception as e:
            print(f"Exception during YouTube search for '{query}': {e}")
            return []