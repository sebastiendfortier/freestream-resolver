"""Vumoo.mx scraper (movie-focused port from Scrubs v2)."""

from __future__ import annotations

import re

import httpx

from freestream_resolver.html_utils import clean_title, parse_dom, remove_tags
from freestream_resolver.http_client import KODI_UA
from freestream_resolver.models import ScrapeRequest, StreamCandidate


class VumooScraper:
    base_link = "https://vumoo.mx"
    search_link = "/search-movies/%s.html"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(timeout=30.0, follow_redirects=True)
        self._own_client = client is None

    def close(self) -> None:
        if self._own_client:
            self._client.close()

    def scrape(self, req: ScrapeRequest) -> list[StreamCandidate]:
        if req.media_type == "tv":
            return []
        slug = re.sub(r"\s+", "+", clean_title(req.title))
        search_url = f"{self.base_link}{self.search_link % slug}"
        html = self._client.get(search_url, headers={"User-Agent": KODI_UA}).text
        blocks = parse_dom(html, "div", attrs={"class": "itemInfo"})
        if not blocks:
            return []

        detail_path = None
        for block in blocks:
            block_html = block if isinstance(block, str) else str(block)
            hrefs = parse_dom(block_html, "a", ret="href")
            if not hrefs:
                continue
            text = remove_tags(block_html).lower()
            if clean_title(req.title) in text:
                detail_path = hrefs[0]
                if req.year and str(req.year) not in text:
                    continue
                break
        if not detail_path:
            return []

        detail_url = detail_path if detail_path.startswith("http") else f"{self.base_link}{detail_path}"
        page = self._client.get(detail_url, headers={"User-Agent": KODI_UA}).text
        lines = parse_dom(page, "div", attrs={"class": "server_line"})
        out: list[StreamCandidate] = []
        for line in lines:
            line_html = line if isinstance(line, str) else str(line)
            hrefs = parse_dom(line_html, "a", ret="href")
            if not hrefs:
                continue
            link = hrefs[0]
            if not link.startswith("http"):
                link = f"{self.base_link}/{link.lstrip('/')}"
            host = remove_tags(line_html).lower() or "vumoo"
            out.append(StreamCandidate(url=link, quality="SD", provider=host[:32]))
        return out
