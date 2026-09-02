"""Parallel scrape orchestration."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError, as_completed

import httpx

from freestream_resolver.hoster_resolve import resolve_all
from freestream_resolver.models import ResolvedStream, ScrapeRequest, StreamCandidate
from freestream_resolver.sites.flixhq import FlixhqScraper
from freestream_resolver.sites.levidia import LevidiaScraper
from freestream_resolver.sites.levidiamovies import LevidiamoviesScraper
from freestream_resolver.sites.movies2watch import Movies2watchScraper
from freestream_resolver.sites.vumoo import VumooScraper
from freestream_resolver.sites.watchseries import WatchseriesScraper

SCRAPERS = [
    LevidiaScraper,
    FlixhqScraper,
    VumooScraper,
    WatchseriesScraper,
    LevidiamoviesScraper,
    Movies2watchScraper,
]

SCRAPER_TIMEOUT_S = 25.0


def collect_candidates(req: ScrapeRequest, timeout: float = 60.0) -> list[StreamCandidate]:
    candidates: list[StreamCandidate] = []

    def run_scraper(scraper_cls: type) -> list[StreamCandidate]:
        scraper = scraper_cls()
        try:
            return scraper.scrape(req)
        finally:
            scraper.close()

    with ThreadPoolExecutor(max_workers=len(SCRAPERS)) as pool:
        futures = {pool.submit(run_scraper, cls): cls for cls in SCRAPERS}
        try:
            for fut in as_completed(futures, timeout=timeout):
                cls = futures[fut]
                try:
                    candidates.extend(fut.result(timeout=SCRAPER_TIMEOUT_S))
                except (FuturesTimeoutError, Exception):
                    fut.cancel()
        except FuturesTimeoutError:
            for fut in futures:
                fut.cancel()

    deduped: list[StreamCandidate] = []
    seen: set[str] = set()
    for c in candidates:
        if c.url and c.url not in seen:
            seen.add(c.url)
            deduped.append(c)
    return deduped


def resolve_request(
    req: ScrapeRequest,
    *,
    use_flare: bool = False,
    client: httpx.Client | None = None,
) -> list[ResolvedStream]:
    own = client is None
    client = client or httpx.Client(timeout=60.0, follow_redirects=True)
    try:
        candidates = collect_candidates(req)
        return resolve_all(client, candidates, use_flare=use_flare)
    finally:
        if own:
            client.close()
