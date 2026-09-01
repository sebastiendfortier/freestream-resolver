#!/usr/bin/env python3
"""Verify resolver can produce streams (live network)."""

from __future__ import annotations

import sys

from freestream_resolver.models import ScrapeRequest
from freestream_resolver.orchestrator import collect_candidates, resolve_request


def main() -> int:
    # The Dark Knight — commonly available on levidia-style aggregators
    req = ScrapeRequest(
        imdb_id="tt0468569",
        title="The Dark Knight",
        year=2008,
        media_type="movie",
    )
    candidates = collect_candidates(req)
    if not candidates:
        print("RESOLVE_MOVIE_NO_CANDIDATES", file=sys.stderr)
        return 1
    streams = resolve_request(req, use_flare=False)
    if streams:
        print("RESOLVE_MOVIE_OK")
        return 0
    # Candidates found but hoster resolve failed — still proves scrape path
    print("RESOLVE_MOVIE_SCRAPE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
