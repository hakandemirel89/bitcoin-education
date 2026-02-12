from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Database
    database_url: str = "sqlite:///data/btcedu.db"

    # ChromaDB
    chromadb_persist_dir: str = "data/chromadb"

    # Podcast Source
    podcast_youtube_channel_id: str = ""
    podcast_rss_url: str = ""

    # Audio
    audio_download_dir: str = "data/audio"
    audio_format: str = "m4a"
    max_audio_chunk_mb: int = 24

    # Content Generation
    claude_model: str = "claude-sonnet-4-20250514"
    max_retries: int = 3

    # Output
    output_dir: str = "output"

    # Whisper
    whisper_model: str = "whisper-1"
    whisper_language: str = "de"

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


def get_settings() -> Settings:
    return Settings()
