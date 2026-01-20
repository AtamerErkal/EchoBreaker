from typing import List, Optional
from pydantic import BaseModel, Field

class VideoMetadata(BaseModel):
    """Details about the original YouTube video."""
    video_title: str = "Unknown Title"
    channel_name: str = "Unknown Channel"
    duration: str = "00:00"
    view_count: str = "0"
    upload_date: str = "Unknown"
    thumbnail: Optional[str] = None
    description: Optional[str] = None

class MinedOpinion(BaseModel):
    """Represents a specific opinion extracted from the transcript."""
    target: str
    assessment: str
    sentiment: str

class ExtractedClaim(BaseModel):
    """A key point or claim identified in the video."""
    text: str
    sentiment: str
    confidence_score: float
    opinions: List[MinedOpinion] = []

class VideoSuggestion(BaseModel):
    """A video suggested as a counter-perspective."""
    title: str
    url: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    channel_name: Optional[str] = None
    view_count: Optional[str] = None  # String format (e.g., "1.5M")
    relevance_score: Optional[float] = None
    description: Optional[str] = None

class CounterArgument(BaseModel):
    """An AI-generated counter-argument with supporting video evidence."""
    type: str = Field(..., description="Type of argument: Ethical, Empirical, or Logical")
    title: str
    content: str
    source_reference: Optional[str] = None
    youtube_query: str = Field(..., description="Search query used to find counter-videos")
    suggested_videos: List[VideoSuggestion] = []
    
    # Academic/Scientific Perspectives
    academic_insight: Optional[str] = Field(None, description="Detailed academic perspective (~150 words)")
    academic_search_query: Optional[str] = Field(None, description="Optimized query for academic sources (e.g., Google Scholar)")

class AnalysisResult(BaseModel):
    """The final structured analysis report."""
    # Metadata Field (Crucial for fixing the ValueError in main.py)
    video_metadata: Optional[VideoMetadata] = None
    
    # Analysis Details
    topic: str = Field(..., description="Short topic summary (3-5 words)")
    primary_claim: str = Field(..., description="The main argument presented in the video")
    
    counter_arguments: List[CounterArgument] = []
    confidence_score: float = 0.0
    processed_at: Optional[str] = None