from typing import List, Optional
from pydantic import BaseModel, Field

class MinedOpinion(BaseModel):
    target: str
    assessment: str
    sentiment: str

class ExtractedClaim(BaseModel):
    text: str
    sentiment: str
    confidence_score: float
    opinions: List[MinedOpinion] = []

class VideoSuggestion(BaseModel):
    title: str
    url: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None  # Duration in seconds
    channel_name: Optional[str] = None
    view_count: Optional[int] = None
    relevance_score: Optional[float] = None  # 0.0-1.0 relevance to counter-argument
    description: Optional[str] = None  # Video description for verification

class CounterArgument(BaseModel):
    type: str = Field(..., description="Type of argument: Ethical, Empirical, or Logical")
    title: str
    content: str
    source_reference: Optional[str] = None
    youtube_query: str = Field(..., description="Search query to find videos supporting this argument")
    suggested_videos: List[VideoSuggestion] = []
    semantic_contrast_score: Optional[float] = None  # How opposed this is to original claim (0.0-1.0)

class AnalysisResult(BaseModel):
    video_url: str
    topic_summary: str
    overall_sentiment: str
    claims: List[ExtractedClaim]
    counter_arguments: List[CounterArgument]
