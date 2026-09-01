"""Levidia.ch site scraper (ported from Scrubs v2)."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlencode

import httpx

from freestream_resolver.html_utils import clean_title, parse_dom, remove_tags
from freestream_resolver.http_client import KODI_UA
from freestream_resolver.models import ScrapeRequest, StreamCandidate


class LevidiaScraper:
    base_link = "https://www.levidia.ch"
    search_link = "/search.php?q=%s"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(timeout=30.0, follow_redirects=True)
        self._own_client = client is None

    def close(self) -> None:
        if self._own_client:
            self._client.close()

    def scrape(self, req: ScrapeRequest) -> list[StreamCandidate]:
        headers = {
            "User-Agent": KODI_UA,
            "Accept": "*/*",
            "Referer": self.base_link,
            "Origin": self.base_link,
        }
        search_url = f"{self.base_link}{self.search_link % req.title}"
        self._client.get(self.base_link, headers=headers)
        r = self._client.post(search_url, headers=headers).text
        blocks = parse_dom(r, "div", attrs={"class": "mainlink"})
        if not blocks:
            return []
        html = blocks[0] if isinstance(blocks[0], str) else str(blocks[0])
        hrefs = parse_dom(html, "a", ret="href")
        labels = [remove_tags(x) for x in parse_dom(html, "a")]
        rows: list[tuple[str, str, str]] = []
        for href, label in zip(hrefs, labels):
            years = re.findall(r"\((\d{4})\)", label)
            if not href or not years:
                continue
            name = re.sub(r"\(\d{4}\)", "", label).strip()
            rows.append((href, name, years[0]))

        title_key = clean_title(req.title)
        match_url = None
        for href, name, yr in rows:
            if clean_title(name) == title_key or title_key in clean_title(name):
                if req.year and str(req.year) != yr:
                    continue
                match_url = href
                break
        if not match_url and rows:
            match_url = rows[0][0]

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
            if not ep_url:
                return []
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
                final = str(resp.url)
                out.append(
                    StreamCandidate(
                        url=final,
                        quality="SD",
                        provider=host or "levidia",
                        direct="wootly" in final.lower(),
                    )
                )
            except Exception:
                continue
        return out
