"""Levidiamovies.club scraper (Levidia mirror)."""

from __future__ import annotations

import re

import httpx

from freestream_resolver.html_utils import clean_title, parse_dom, remove_tags
from freestream_resolver.http_client import KODI_UA
from freestream_resolver.models import ScrapeRequest, StreamCandidate


class LevidiamoviesScraper:
    base_link = "https://www.levidiamovies.club"
    search_link = "/search.php?q=%s"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(timeout=30.0, follow_redirects=True)
        self._own_client = client is None

    def close(self) -> None:
        if self._own_client:
            self._client.close()

    def scrape(self, req: ScrapeRequest) -> list[StreamCandidate]:
        headers = {"User-Agent": KODI_UA, "Referer": self.base_link}
        search_url = f"{self.base_link}{self.search_link % req.title}"
        try:
            self._client.get(self.base_link, headers=headers)
            html = self._client.post(search_url, headers=headers).text
        except Exception:
            return []

        blocks = parse_dom(html, "div", attrs={"class": "mainlink"})
        if not blocks:
            return []
        block = blocks[0] if isinstance(blocks[0], str) else str(blocks[0])
        hrefs = parse_dom(block, "a", ret="href")
        labels = [remove_tags(x) for x in parse_dom(block, "a")]
        title_key = clean_title(req.title)
        match_url = None
        for href, label in zip(hrefs, labels):
            years = re.findall(r"\((\d{4})\)", label)
            name = re.sub(r"\(\d{4}\)", "", label).strip()
            if title_key in clean_title(name) or clean_title(name) in title_key:
                if req.year and years and str(req.year) != years[0]:
                    continue
                match_url = href
                break
        if not match_url and hrefs:
            match_url = hrefs[0]
        if not match_url:
            return []
        if not match_url.startswith("http"):
            match_url = f"{self.base_link}/{match_url.lstrip('/')}"

        if req.media_type == "tv" and req.season:
            match_url = f"{match_url}&s={req.season}"
        page = self._client.get(match_url, headers=headers).text

        if req.media_type == "tv" and req.season and req.episode:
            seaepi = f"s{req.season}e{req.episode}"
            items = list(zip(parse_dom(page, "a", ret="href"), parse_dom(page, "a")))
            ep_url = next((h for h, _ in items if seaepi in h.lower()), None)
            if ep_url:
                if not ep_url.startswith("http"):
                    ep_url = f"{self.base_link}/{ep_url.lstrip('/')}"
                page = self._client.get(ep_url, headers=headers).text
            hosts = [remove_tags(x) for x in parse_dom(page, "span", attrs={"class": "kiri xxx1 xx12"})]
            links = parse_dom(page, "a", attrs={"class": "xxx xflv"}, ret="href")
        else:
            hosts = [remove_tags(x) for x in parse_dom(page, "span", attrs={"class": "kiri xxx1"})]
            links = parse_dom(page, "a", attrs={"class": "xxx xflv"}, ret="href")

        out: list[StreamCandidate] = []
        for host, link in zip(hosts, links):
            if not link:
                continue
            if not link.startswith("http"):
                link = f"{self.base_link}/{link.lstrip('/')}"
            try:
                resp = self._client.get(link, headers=headers)
                out.append(
                    StreamCandidate(
                        url=str(resp.url),
                        quality="SD",
                        provider=host or "levidiamovies",
                        direct="wootly" in str(resp.url).lower(),
                    )
                )
            except Exception:
                continue
        return out
