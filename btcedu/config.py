from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    whisper_api_key: str = ""  # falls back to openai_api_key if empty

    # Database
    database_url: str = "sqlite:///data/btcedu.db"

    # ChromaDB (optional)
    use_chroma: bool = False
    chromadb_persist_dir: str = "data/chromadb"

    # Podcast Source
    source_type: str = "youtube_rss"  # "youtube_rss" or "rss"
    podcast_youtube_channel_id: str = ""
    podcast_rss_url: str = ""

    # Audio / Raw Data
    raw_data_dir: str = "data/raw"
    audio_format: str = "m4a"
    max_audio_chunk_mb: int = 24

    # Transcription
    transcripts_dir: str = "data/transcripts"
    whisper_model: str = "whisper-1"
    whisper_language: str = "de"

    # Chunking
    chunks_dir: str = "data/chunks"
    chunk_size: int = 1500  # chars (~350 tokens)
    chunk_overlap: float = 0.15  # 15% overlap

    # Content Generation
    claude_model: str = "claude-sonnet-4-20250514"
    max_retries: int = 3

    # Output
    output_dir: str = "output"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def rss_url(self) -> str:
        if self.podcast_rss_url:
            return self.podcast_rss_url
        if self.podcast_youtube_channel_id:
            return (
                f"https://www.youtube.com/feeds/videos.xml"
                f"?channel_id={self.podcast_youtube_channel_id}"
            )
        return ""

    @property
    def effective_whisper_api_key(self) -> str:
        return self.whisper_api_key or self.openai_api_key


def get_settings() -> Settings:
    return Settings()
