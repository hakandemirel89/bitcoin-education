import hashlib
from datetime import datetime, timezone

import feedparser

from btcedu.models.schemas import EpisodeInfo


def _struct_to_datetime(st: object) -> datetime | None:
    """Convert feedparser's time.struct_time to timezone-aware datetime."""
    if st is None:
        return None
    try:
        from calendar import timegm
        return datetime.fromtimestamp(timegm(st), tz=timezone.utc)
    except Exception:
        return None


def _extract_youtube_video_id(entry: dict) -> str | None:
    """Extract YouTube video ID from a feed entry."""
    # feedparser exposes yt:videoId as yt_videoid
    vid = getattr(entry, "yt_videoid", None)
    if vid:
        return vid
    # Fallback: parse from link URL
    link = entry.get("link", "")
    if "youtube.com/watch" in link and "v=" in link:
        return link.split("v=")[1].split("&")[0]
    return None


def _make_fallback_id(url: str) -> str:
    """Generate a stable episode ID from a URL via sha1."""
    return hashlib.sha1(url.encode()).hexdigest()[:12]


def parse_youtube_rss(feed_content: str) -> list[EpisodeInfo]:
    """Parse a YouTube channel Atom feed and return episode info list."""
    feed = feedparser.parse(feed_content)
    episodes = []
    for entry in feed.entries:
        video_id = _extract_youtube_video_id(entry)
        if not video_id:
            continue
        link = entry.get("link", f"https://www.youtube.com/watch?v={video_id}")
        published = _struct_to_datetime(entry.get("published_parsed"))
        episodes.append(
            EpisodeInfo(
                episode_id=video_id,
                title=entry.get("title", "Untitled"),
                published_at=published,
                url=link,
                source="youtube_rss",
            )
        )
    return episodes


def parse_rss(feed_content: str) -> list[EpisodeInfo]:
    """Parse a generic RSS/Atom feed and return episode info list."""
    feed = feedparser.parse(feed_content)
    episodes = []
    for entry in feed.entries:
        link = entry.get("link", "")
        if not link:
            continue
        episode_id = _make_fallback_id(link)
        published = _struct_to_datetime(entry.get("published_parsed"))
        episodes.append(
            EpisodeInfo(
                episode_id=episode_id,
                title=entry.get("title", "Untitled"),
                published_at=published,
                url=link,
                source="rss",
            )
        )
    return episodes


def fetch_feed(url: str, timeout: int = 30) -> str:
    """Fetch RSS/Atom feed content from a URL.

    Uses feedparser's built-in HTTP fetching but returns raw content
    for testability. In practice, we parse directly.
    """
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "btcedu/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def parse_feed(feed_content: str, source_type: str) -> list[EpisodeInfo]:
    """Parse feed content based on source type."""
    if source_type == "youtube_rss":
        return parse_youtube_rss(feed_content)
    return parse_rss(feed_content)
