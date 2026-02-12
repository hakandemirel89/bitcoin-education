import os

from btcedu.config import Settings


class TestSettings:
    def test_default_values(self):
        settings = Settings(
            anthropic_api_key="test-key",
            openai_api_key="test-key",
            podcast_youtube_channel_id="UCtest123",
        )
        assert settings.database_url == "sqlite:///data/btcedu.db"
        assert settings.chromadb_persist_dir == "data/chromadb"
        assert settings.audio_format == "m4a"
        assert settings.max_audio_chunk_mb == 24
        assert settings.claude_model == "claude-sonnet-4-20250514"
        assert settings.max_retries == 3
        assert settings.whisper_model == "whisper-1"
        assert settings.whisper_language == "de"
        assert settings.output_dir == "output"

    def test_rss_url_from_channel_id(self):
        settings = Settings(
            anthropic_api_key="test-key",
            openai_api_key="test-key",
            podcast_youtube_channel_id="UCtest123",
        )
        expected = "https://www.youtube.com/feeds/videos.xml?channel_id=UCtest123"
        assert settings.rss_url == expected

    def test_rss_url_explicit_override(self):
        settings = Settings(
            anthropic_api_key="test-key",
            openai_api_key="test-key",
            podcast_youtube_channel_id="UCtest123",
            podcast_rss_url="https://custom.feed/rss",
        )
        assert settings.rss_url == "https://custom.feed/rss"

    def test_rss_url_empty_when_no_channel(self):
        settings = Settings(
            anthropic_api_key="test-key",
            openai_api_key="test-key",
        )
        assert settings.rss_url == ""
