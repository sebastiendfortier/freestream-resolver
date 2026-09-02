#!/usr/bin/env python3
"""Verify TV scrape path returns candidates."""

from __future__ import annotations

import sys

from freestream_resolver.models import ScrapeRequest
from freestream_resolver.orchestrator import collect_candidates


def main() -> int:
    req = ScrapeRequest(
        imdb_id="tt0903747",
        title="Breaking Bad",
        year=2008,
        media_type="tv",
        season=1,
        episode=1,
    )
    candidates = collect_candidates(req)
    if candidates:
        print("RESOLVE_TV_OK")
        return 0
    print("RESOLVE_TV_NO_CANDIDATES", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
