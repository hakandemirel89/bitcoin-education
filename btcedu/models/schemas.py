from datetime import datetime

from pydantic import BaseModel, Field


class EpisodeInfo(BaseModel):
    """Parsed episode info from RSS/YouTube feed."""

    episode_id: str
    title: str
    published_at: datetime | None = None
    url: str
    source: str = "youtube_rss"


class TranscriptChunk(BaseModel):
    """A chunk of transcript text with metadata."""

    chunk_index: int
    text: str
    word_count: int
    start_sentence: int
    end_sentence: int
    episode_video_id: str


class RetrievedChunk(BaseModel):
    """A chunk retrieved from ChromaDB with similarity score."""

    chunk_index: int
    text: str
    score: float = 0.0
    metadata: dict = Field(default_factory=dict)


class Citation(BaseModel):
    """A citation mapping from generated content to source chunk."""

    output_file: str
    section: str
    cited_text_de: str
    chunk_index: int


class ContentPackage(BaseModel):
    """Complete content package for one episode."""

    episode_video_id: str
    outline: str = ""
    script: str = ""
    shorts: str = ""
    visuals: str = ""
    qa_report: str = ""
    publishing: str = ""
    citations: list[Citation] = Field(default_factory=list)


class PipelineStatus(BaseModel):
    """Status summary for an episode's pipeline progress."""

    episode_id: int
    video_id: str
    title: str
    status: str
    detected_at: datetime
    completed_at: datetime | None = None
    error_message: str | None = None
    total_cost_usd: float = 0.0
