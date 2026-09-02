"""FlixHQ.to scraper (movie + TV, ported from Scrubs v2)."""

from __future__ import annotations

import json
import re

import httpx

from freestream_resolver.html_utils import clean_title, parse_dom
from freestream_resolver.http_client import KODI_UA
from freestream_resolver.models import ScrapeRequest, StreamCandidate


class FlixhqScraper:
    base_link = "https://flixhq.to"
    search_link = "/search/%s"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(timeout=30.0, follow_redirects=True)
        self._own_client = client is None

    def close(self) -> None:
        if self._own_client:
            self._client.close()

    def _headers(self) -> dict[str, str]:
        return {"User-Agent": KODI_UA, "Referer": self.base_link, "X-Requested-With": "XMLHttpRequest"}

    def scrape(self, req: ScrapeRequest) -> list[StreamCandidate]:
        slug = re.sub(r"[^a-z0-9]+", "-", clean_title(req.title)).strip("-")
        search_url = f"{self.base_link}{self.search_link % slug}"
        html = self._client.get(search_url, headers=self._headers()).text
        items = parse_dom(html, "div", attrs={"class": "flw-item"})
        if not items:
            return []

        hrefs: list[str] = []
        titles: list[str] = []
        for block in items:
            block_html = block if isinstance(block, str) else str(block)
            h = parse_dom(block_html, "a", ret="href")
            t = parse_dom(block_html, "a", ret="title")
            if h and t:
                hrefs.append(h[0])
                titles.append(t[0])

        detail_path = None
        title_key = clean_title(req.title)
        for href, name in zip(hrefs, titles):
            if title_key not in clean_title(name):
                continue
            if req.media_type == "tv" and not href.startswith("/tv/"):
                continue
            if req.media_type == "movie" and not href.startswith("/movie/"):
                continue
            detail_path = href
            break
        if not detail_path and hrefs:
            detail_path = hrefs[0]

        if not detail_path:
            return []
        detail_url = f"{self.base_link}{detail_path}"
        page = self._client.get(detail_url, headers=self._headers()).text
        data_ids = parse_dom(page, "div", ret="data-id")
        if not data_ids:
            return []
        item_id = data_ids[0]

        server_ids: list[str] = []
        if req.media_type == "tv" and req.season and req.episode:
            seasons = self._client.get(
                f"{self.base_link}/ajax/season/list/{item_id}", headers=self._headers()
            ).text
            season_ids = parse_dom(seasons, "a", ret="data-id")
            season_labels = [str(x) for x in parse_dom(seasons, "a")]
            season_id = None
            for sid, label in zip(season_ids, season_labels):
                if f"season {req.season}".lower() in label.lower():
                    season_id = sid
                    break
            if not season_id and season_ids:
                season_id = season_ids[min(req.season - 1, len(season_ids) - 1)]
            if not season_id:
                return []
            eps = self._client.get(
                f"{self.base_link}/ajax/season/episodes/{season_id}", headers=self._headers()
            ).text
            ep_ids = parse_dom(eps, "a", ret="data-id")
            ep_titles = [str(x) for x in parse_dom(eps, "a", ret="title")]
            ep_id = None
            for eid, et in zip(ep_ids, ep_titles):
                if f"eps {req.episode}".lower() in et.lower() or f"e{req.episode}" in et.lower():
                    ep_id = eid
                    break
            if not ep_id and ep_ids:
                ep_id = ep_ids[min(req.episode - 1, len(ep_ids) - 1)]
            if not ep_id:
                return []
            servers = self._client.get(
                f"{self.base_link}/ajax/episode/servers/{ep_id}", headers=self._headers()
            ).text
            server_ids = parse_dom(servers, "a", ret="data-id")
        else:
            servers = self._client.get(
                f"{self.base_link}/ajax/episode/list/{item_id}", headers=self._headers()
            ).text
            server_ids = parse_dom(servers, "a", ret="data-linkid") or parse_dom(servers, "a", ret="data-id")

        out: list[StreamCandidate] = []
        for sid in server_ids[:8]:
            try:
                resp = self._client.get(f"{self.base_link}/ajax/get_link/{sid}", headers=self._headers())
                payload = resp.json()
                link = payload.get("link") or ""
                if link:
                    out.append(StreamCandidate(url=link, quality="HD", provider="flixhq"))
            except Exception:
                continue
        return out
