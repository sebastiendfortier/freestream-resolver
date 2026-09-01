"""Data models for stream resolution."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StreamCandidate:
    url: str
    quality: str = "SD"
    provider: str = ""
    direct: bool = False
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class ResolvedStream:
    stream_url: str
    quality: str = "SD"
    headers: dict[str, str] = field(default_factory=dict)
    content_type: str = ""
    provider: str = ""
    source_url: str = ""


@dataclass
class ScrapeRequest:
    imdb_id: str
    title: str
    year: int | None = None
    media_type: str = "movie"  # movie | tv
    season: int | None = None
    episode: int | None = None
