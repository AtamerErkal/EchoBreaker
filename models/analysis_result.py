from typing import List, Optional
from pydantic import BaseModel, Field


class VideoMetadata(BaseModel):
    video_title: str = "Unknown Title"
    channel_name: str = "Unknown Channel"
    duration: str = "00:00"
    duration_seconds: Optional[int] = None
    view_count: str = "0"
    view_count_raw: Optional[int] = None
    upload_date: str = "Unknown"
    thumbnail: Optional[str] = None
    description: Optional[str] = None


class VideoSuggestion(BaseModel):
    title: str
    url: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    channel_name: Optional[str] = None
    view_count: Optional[int] = None
    relevance_score: Optional[float] = None
    description: Optional[str] = None


class CounterArgument(BaseModel):
    type: str = Field(..., description="Ethical, Empirical, or Logical")
    title: str
    content: str
    source_reference: Optional[str] = None
    youtube_query: str = Field(..., description="Search query for counter-videos")
    suggested_videos: List[VideoSuggestion] = []
    semantic_contrast_score: Optional[float] = None
    academic_insight: Optional[str] = None
    source_link: Optional[str] = None


class AnalysisResult(BaseModel):
    video_url: str = ""
    video_metadata: Optional[VideoMetadata] = None
    topic: str = Field(..., description="3-5 word topic summary")
    primary_claim: str = Field(..., description="Main argument of the video")
    overall_sentiment: str = "neutral"
    counter_arguments: List[CounterArgument] = []
    confidence_score: float = 0.0
    processed_at: Optional[str] = None
