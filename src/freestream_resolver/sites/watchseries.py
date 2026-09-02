"""WatchSeries.cyou scraper (direct URL pattern)."""

from __future__ import annotations

import re

import httpx

from freestream_resolver.embed_chain import extract_media_urls
from freestream_resolver.html_utils import clean_title, parse_dom
from freestream_resolver.http_client import KODI_UA, get
from freestream_resolver.models import ScrapeRequest, StreamCandidate


class WatchseriesScraper:
    base_link = "https://watchseries.cyou"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(timeout=30.0, follow_redirects=True)
        self._own_client = client is None

    def close(self) -> None:
        if self._own_client:
            self._client.close()

    def scrape(self, req: ScrapeRequest) -> list[StreamCandidate]:
        slug = re.sub(r"[^a-z0-9]+", "-", clean_title(req.title)).strip("-")
        if req.media_type == "tv" and req.season and req.episode:
            url = f"{self.base_link}/tv-series/{slug}-season-{req.season}-episode-{req.episode}/"
        elif req.year:
            url = f"{self.base_link}/movies/{slug}-{req.year}/"
        else:
            url = f"{self.base_link}/movies/{slug}/"

        headers = {"User-Agent": KODI_UA, "Referer": self.base_link}
        try:
            resp = get(self._client, url, headers=headers)
        except Exception:
            return []

        out: list[StreamCandidate] = []
        for src in parse_dom(resp.text, "iframe", ret="src"):
            link = src if src.startswith("http") else f"{self.base_link}{src}"
            out.append(StreamCandidate(url=link, quality="SD", provider="watchseries"))
        for media in extract_media_urls(resp.text):
            out.append(StreamCandidate(url=media, quality="HD", provider="watchseries", direct=True))
        return out
