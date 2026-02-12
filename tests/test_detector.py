"""Phase 2 tests: feed parsing, detection (idempotent), download."""
import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

from btcedu.core.detector import detect_from_content, download_episode
from btcedu.models.episode import Episode, EpisodeStatus
from btcedu.models.schemas import EpisodeInfo
from btcedu.services.feed_service import (
    _make_fallback_id,
    parse_feed,
    parse_rss,
    parse_youtube_rss,
)

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_FEED = (FIXTURES / "sample_youtube_feed.xml").read_text()


# ── Feed parsing: YouTube RSS ──────────────────────────────────────


class TestParseYoutubeRSS:
    def test_returns_correct_count(self):
        episodes = parse_youtube_rss(SAMPLE_FEED)
        assert len(episodes) == 3

    def test_extracts_video_id(self):
        episodes = parse_youtube_rss(SAMPLE_FEED)
        ids = [ep.episode_id for ep in episodes]
        assert "dQw4w9WgXcQ" in ids
        assert "xYz789AbCdE" in ids
        assert "aBcDeFgHiJk" in ids

    def test_extracts_title(self):
        episodes = parse_youtube_rss(SAMPLE_FEED)
        ep = next(e for e in episodes if e.episode_id == "dQw4w9WgXcQ")
        assert "Bitcoin und die Zukunft des Geldes" in ep.title

    def test_extracts_url(self):
        episodes = parse_youtube_rss(SAMPLE_FEED)
        ep = next(e for e in episodes if e.episode_id == "dQw4w9WgXcQ")
        assert ep.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def test_extracts_published_date(self):
        episodes = parse_youtube_rss(SAMPLE_FEED)
        ep = next(e for e in episodes if e.episode_id == "dQw4w9WgXcQ")
        assert ep.published_at is not None
        assert ep.published_at.year == 2024
        assert ep.published_at.month == 6
        assert ep.published_at.day == 15

    def test_source_is_youtube_rss(self):
        episodes = parse_youtube_rss(SAMPLE_FEED)
        for ep in episodes:
            assert ep.source == "youtube_rss"

    def test_empty_feed(self):
        empty = '<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
        episodes = parse_youtube_rss(empty)
        assert episodes == []


# ── Feed parsing: generic RSS ──────────────────────────────────────


GENERIC_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Podcast</title>
    <item>
      <title>Episode One</title>
      <link>https://example.com/ep1</link>
      <pubDate>Mon, 10 Jun 2024 10:00:00 +0000</pubDate>
    </item>
    <item>
      <title>Episode Two</title>
      <link>https://example.com/ep2</link>
      <pubDate>Mon, 03 Jun 2024 10:00:00 +0000</pubDate>
    </item>
  </channel>
</rss>"""


class TestParseGenericRSS:
    def test_returns_correct_count(self):
        episodes = parse_rss(GENERIC_RSS)
        assert len(episodes) == 2

    def test_uses_sha1_fallback_id(self):
        episodes = parse_rss(GENERIC_RSS)
        expected_id = hashlib.sha1(b"https://example.com/ep1").hexdigest()[:12]
        assert episodes[0].episode_id == expected_id

    def test_source_is_rss(self):
        episodes = parse_rss(GENERIC_RSS)
        for ep in episodes:
            assert ep.source == "rss"

    def test_extracts_title(self):
        episodes = parse_rss(GENERIC_RSS)
        assert episodes[0].title == "Episode One"


# ── parse_feed dispatcher ──────────────────────────────────────────


class TestParseFeed:
    def test_dispatches_youtube_rss(self):
        episodes = parse_feed(SAMPLE_FEED, "youtube_rss")
        assert len(episodes) == 3
        assert episodes[0].source == "youtube_rss"

    def test_dispatches_generic_rss(self):
        episodes = parse_feed(GENERIC_RSS, "rss")
        assert len(episodes) == 2
        assert episodes[0].source == "rss"


# ── Fallback ID helper ─────────────────────────────────────────────


class TestFallbackId:
    def test_deterministic(self):
        id1 = _make_fallback_id("https://example.com/ep1")
        id2 = _make_fallback_id("https://example.com/ep1")
        assert id1 == id2

    def test_length_12(self):
        fid = _make_fallback_id("https://example.com/ep1")
        assert len(fid) == 12

    def test_different_urls_different_ids(self):
        id1 = _make_fallback_id("https://example.com/ep1")
        id2 = _make_fallback_id("https://example.com/ep2")
        assert id1 != id2


# ── Detection: idempotent DB inserts ───────────────────────────────


class TestDetectFromContent:
    def test_inserts_new_episodes(self, db_session):
        result = detect_from_content(db_session, SAMPLE_FEED, "youtube_rss")
        assert result.found == 3
        assert result.new == 3
        assert result.total == 3
        assert db_session.query(Episode).count() == 3

    def test_idempotent_second_run(self, db_session):
        detect_from_content(db_session, SAMPLE_FEED, "youtube_rss")
        result = detect_from_content(db_session, SAMPLE_FEED, "youtube_rss")
        assert result.found == 3
        assert result.new == 0
        assert result.total == 3
        assert db_session.query(Episode).count() == 3

    def test_new_episodes_have_status_new(self, db_session):
        detect_from_content(db_session, SAMPLE_FEED, "youtube_rss")
        episodes = db_session.query(Episode).all()
        for ep in episodes:
            assert ep.status == EpisodeStatus.NEW

    def test_stores_correct_fields(self, db_session):
        detect_from_content(db_session, SAMPLE_FEED, "youtube_rss")
        ep = (
            db_session.query(Episode)
            .filter(Episode.episode_id == "dQw4w9WgXcQ")
            .first()
        )
        assert ep is not None
        assert "Bitcoin und die Zukunft des Geldes" in ep.title
        assert ep.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert ep.source == "youtube_rss"
        assert ep.published_at is not None

    def test_incremental_detection(self, db_session):
        """Detect 3, then add 1 new entry — only the new one is inserted."""
        detect_from_content(db_session, SAMPLE_FEED, "youtube_rss")

        # Feed with one extra episode
        extra_feed = SAMPLE_FEED.replace(
            "</feed>",
            """
  <entry>
    <id>yt:video:newEpisode01</id>
    <yt:videoId>newEpisode01</yt:videoId>
    <title>Neue Episode</title>
    <link rel="alternate" href="https://www.youtube.com/watch?v=newEpisode01"/>
    <published>2024-06-22T10:00:00+00:00</published>
  </entry>
</feed>""",
        )
        result = detect_from_content(db_session, extra_feed, "youtube_rss")
        assert result.found == 4
        assert result.new == 1
        assert result.total == 4


# ── Download: correct path + force flag ────────────────────────────


class TestDownloadEpisode:
    def _make_settings(self, tmp_path):
        from btcedu.config import Settings

        return Settings(
            raw_data_dir=str(tmp_path / "raw"),
            audio_format="m4a",
        )

    def _seed_episode(self, db_session, episode_id="dQw4w9WgXcQ"):
        ep = Episode(
            episode_id=episode_id,
            source="youtube_rss",
            title="Test Episode",
            url=f"https://www.youtube.com/watch?v={episode_id}",
            status=EpisodeStatus.NEW,
        )
        db_session.add(ep)
        db_session.commit()
        return ep

    @patch("btcedu.services.download_service.download_audio")
    def test_creates_correct_path(self, mock_dl, db_session, tmp_path):
        settings = self._make_settings(tmp_path)
        self._seed_episode(db_session)

        expected_dir = str(tmp_path / "raw" / "dQw4w9WgXcQ")
        mock_dl.return_value = f"{expected_dir}/audio.m4a"

        path = download_episode(db_session, "dQw4w9WgXcQ", settings)

        mock_dl.assert_called_once_with(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            output_dir=expected_dir,
            audio_format="m4a",
        )
        assert path == f"{expected_dir}/audio.m4a"

    @patch("btcedu.services.download_service.download_audio")
    def test_updates_status_to_downloaded(self, mock_dl, db_session, tmp_path):
        settings = self._make_settings(tmp_path)
        self._seed_episode(db_session)
        mock_dl.return_value = "/some/path/audio.m4a"

        download_episode(db_session, "dQw4w9WgXcQ", settings)

        ep = db_session.query(Episode).filter(Episode.episode_id == "dQw4w9WgXcQ").first()
        assert ep.status == EpisodeStatus.DOWNLOADED
        assert ep.audio_path == "/some/path/audio.m4a"

    @patch("btcedu.services.download_service.download_audio")
    def test_skips_if_already_downloaded(self, mock_dl, db_session, tmp_path):
        settings = self._make_settings(tmp_path)
        ep = self._seed_episode(db_session)

        # Simulate already downloaded
        audio_file = tmp_path / "raw" / "dQw4w9WgXcQ" / "audio.m4a"
        audio_file.parent.mkdir(parents=True)
        audio_file.write_text("fake audio")
        ep.audio_path = str(audio_file)
        ep.status = EpisodeStatus.DOWNLOADED
        db_session.commit()

        path = download_episode(db_session, "dQw4w9WgXcQ", settings)

        mock_dl.assert_not_called()
        assert path == str(audio_file)

    @patch("btcedu.services.download_service.download_audio")
    def test_force_redownloads(self, mock_dl, db_session, tmp_path):
        settings = self._make_settings(tmp_path)
        ep = self._seed_episode(db_session)

        # Simulate already downloaded
        audio_file = tmp_path / "raw" / "dQw4w9WgXcQ" / "audio.m4a"
        audio_file.parent.mkdir(parents=True)
        audio_file.write_text("fake audio")
        ep.audio_path = str(audio_file)
        ep.status = EpisodeStatus.DOWNLOADED
        db_session.commit()

        mock_dl.return_value = str(audio_file)
        download_episode(db_session, "dQw4w9WgXcQ", settings, force=True)

        mock_dl.assert_called_once()

    def test_raises_for_unknown_episode(self, db_session, tmp_path):
        settings = self._make_settings(tmp_path)
        import pytest

        with pytest.raises(ValueError, match="Episode not found"):
            download_episode(db_session, "nonexistent", settings)
