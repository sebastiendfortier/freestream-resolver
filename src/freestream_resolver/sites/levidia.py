"""Levidia.ch site scraper (ported from Scrubs v2)."""

from __future__ import annotations

import re

import httpx

from freestream_resolver.hosters.wootly import normalize_wootly_url
from freestream_resolver.html_utils import clean_title, parse_dom, remove_tags
from freestream_resolver.http_client import KODI_UA
from freestream_resolver.models import ScrapeRequest, StreamCandidate

_CHK_RE = re.compile(r"""_3chk\(['\"](.+?)['\"],['\"](.+?)['\"]\)""")


class LevidiaScraper:
    base_link = "https://www.levidia.ch"
    search_link = "/search.php?q=%s"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(timeout=30.0, follow_redirects=True)
        self._own_client = client is None

    def close(self) -> None:
        if self._own_client:
            self._client.close()

    def _headers(self, *, referer: str | None = None) -> dict[str, str]:
        hdrs = {
            "User-Agent": KODI_UA,
            "Accept": "text/html,application/xhtml+xml",
            "Referer": referer or self.base_link,
        }
        return hdrs

    def _cookie_header(self, page_html: str) -> str:
        cookies = dict(self._client.cookies)
        match = _CHK_RE.search(page_html)
        if match:
            cookies[match.group(1)] = match.group(2)
        return "; ".join(f"{k}={v}" for k, v in cookies.items())

    def _normalize_hoster_url(self, url: str) -> str:
        if url.startswith("//"):
            url = "https:" + url
        return normalize_wootly_url(url)

    def _resolve_go_link(self, go_url: str, *, referer: str, cookie_header: str) -> str | None:
        if not go_url or "go.php" not in go_url:
            return go_url or None
        headers = {
            **self._headers(referer=referer),
            "Cookie": cookie_header,
        }
        try:
            resp = self._client.get(go_url, headers=headers, follow_redirects=False)
        except Exception:
            return None
        if resp.status_code in (301, 302, 303, 307, 308):
            loc = resp.headers.get("location") or ""
            if not loc:
                return None
            if loc.startswith("//"):
                loc = "https:" + loc
            return self._normalize_hoster_url(loc)
        final = str(resp.url)
        if "go.php" in final:
            return None
        return self._normalize_hoster_url(final)

    def _collect_hoster_links(self, page: str, *, referer: str) -> list[tuple[str, str]]:
        hosts = [remove_tags(x) for x in parse_dom(page, "span", attrs={"class": "kiri xxx1 xx12"})]
        if not hosts:
            hosts = [remove_tags(x) for x in parse_dom(page, "span", attrs={"class": "kiri xxx1"})]
        links = parse_dom(page, "a", attrs={"class": "xxx xflv"}, ret="href")
        if not links:
            links = [
                href
                for href in parse_dom(page, "a", attrs={"target": "_blank"}, ret="href")
                if href and "imdb" not in href
            ]
        cookie_header = self._cookie_header(page)
        rows: list[tuple[str, str]] = []
        for host, link in zip(hosts, links):
            if not link:
                continue
            if not link.startswith("http"):
                link = f"{self.base_link}/{link.lstrip('/')}"
            final = self._resolve_go_link(link, referer=referer, cookie_header=cookie_header)
            if final:
                rows.append((host or "levidia", final))
        return rows

    def scrape(self, req: ScrapeRequest) -> list[StreamCandidate]:
        headers = self._headers()
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

        referer = match_url
        if req.media_type == "tv" and req.season and req.episode:
            seaepi = f"s{req.season}e{req.episode}"
            items = list(zip(parse_dom(page, "a", ret="href"), parse_dom(page, "a")))
            ep_pat = re.compile(rf"s{req.season}e{req.episode}(?!\d)", re.I)
            ep_url = next((h for h, _ in items if h and ep_pat.search(h)), None)
            if not ep_url:
                return []
            if not ep_url.startswith("http"):
                ep_url = f"{self.base_link}/{ep_url.lstrip('/')}"
            referer = ep_url
            page = self._client.get(ep_url, headers=self._headers(referer=match_url)).text

        host_links = self._collect_hoster_links(page, referer=referer)
        out: list[StreamCandidate] = []
        for host, final in host_links:
            out.append(
                StreamCandidate(
                    url=final,
                    quality="HD" if "wootly" in final.lower() else "SD",
                    provider=host or "levidia",
                    direct="wootly" in final.lower(),
                )
            )
        return out

    def list_episodes(self, req: ScrapeRequest) -> list[dict[str, str | int]]:
        """Return season episodes from the series page (Levidia TV layout)."""
        if req.media_type != "tv" or not req.season:
            return []
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
        match_url = f"{match_url}&s={req.season}"
        page = self._client.get(match_url, headers=headers).text
        seaepi_prefix = f"s{req.season}e"
        items = list(zip(parse_dom(page, "a", ret="href"), parse_dom(page, "a")))
        out: list[dict[str, str | int]] = []
        seen: set[int] = set()
        for href, label in items:
            href_l = (href or "").lower()
            if seaepi_prefix not in href_l:
                continue
            m = re.search(rf"s{req.season}e(\d+)", href_l)
            if not m:
                continue
            ep_num = int(m.group(1))
            if ep_num in seen:
                continue
            seen.add(ep_num)
            out.append(
                {
                    "season": req.season,
                    "episode": ep_num,
                    "title": remove_tags(label) or f"Episode {ep_num}",
                }
            )
        out.sort(key=lambda row: int(row["episode"]))
        return out
