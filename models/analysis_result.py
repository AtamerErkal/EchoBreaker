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
    title: str = Field(..., description="Punchy title, under 10 words")
    key_point: str = Field(..., description="2 sentences max")
    why_it_matters: str = Field("", description="1 sentence, real-world impact")
    academic_ref: str = Field("", description="Author, Work (Year)")
    youtube_query: str = Field("", description="Search terms for YouTube")
    youtube_search_url: Optional[str] = None
    scholar_search_url: Optional[str] = None
    suggested_videos: List[VideoSuggestion] = []


class AnalysisResult(BaseModel):
    video_url: str = ""
    video_metadata: Optional[VideoMetadata] = None
    topic: str = Field(..., description="3-5 word topic summary")
    primary_claim: str = Field(..., description="Main argument of the video")
    echo_chamber_query: str = Field("", description="Search terms that would reinforce the video's viewpoint")
    echo_chamber_description: str = Field("", description="1 sentence explaining what the algorithm would keep showing")
    counter_arguments: List[CounterArgument] = []
    confidence_score: float = 0.0
