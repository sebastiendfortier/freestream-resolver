"""Movies2watch.tv scraper (search + embed links)."""

from __future__ import annotations

import re

import httpx

from freestream_resolver.embed_chain import extract_media_urls
from freestream_resolver.html_utils import clean_title, parse_dom
from freestream_resolver.http_client import KODI_UA, get
from freestream_resolver.models import ScrapeRequest, StreamCandidate


class Movies2watchScraper:
    base_link = "https://movies2watch.tv"
    search_link = "/search/%s"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(timeout=30.0, follow_redirects=True)
        self._own_client = client is None

    def close(self) -> None:
        if self._own_client:
            self._client.close()

    def scrape(self, req: ScrapeRequest) -> list[StreamCandidate]:
        slug = re.sub(r"[^a-z0-9]+", "-", clean_title(req.title)).strip("-")
        search_url = f"{self.base_link}{self.search_link % slug}"
        headers = {"User-Agent": KODI_UA, "Referer": self.base_link}
        try:
            resp = get(self._client, search_url, headers=headers)
        except Exception:
            return []

        cards = parse_dom(resp.text, "div", attrs={"class": "flw-item"})
        detail_path = None
        for card in cards:
            card_html = card if isinstance(card, str) else str(card)
            hrefs = parse_dom(card_html, "a", ret="href")
            titles = parse_dom(card_html, "a", ret="title")
            if not hrefs:
                continue
            title = titles[0] if titles else ""
            if clean_title(req.title) in clean_title(title):
                if req.media_type == "tv" and "/tv/" not in hrefs[0]:
                    continue
                if req.media_type == "movie" and "/movie/" not in hrefs[0]:
                    continue
                detail_path = hrefs[0]
                break
        if not detail_path:
            return []

        detail_url = detail_path if detail_path.startswith("http") else f"{self.base_link}{detail_path}"
        try:
            page = get(self._client, detail_url, headers=headers).text
        except Exception:
            return []

        out: list[StreamCandidate] = []
        for src in parse_dom(page, "iframe", ret="src"):
            link = src if src.startswith("http") else f"{self.base_link}{src}"
            out.append(StreamCandidate(url=link, quality="SD", provider="movies2watch"))
        for media in extract_media_urls(page):
            out.append(StreamCandidate(url=media, quality="HD", provider="movies2watch", direct=True))
        return out
