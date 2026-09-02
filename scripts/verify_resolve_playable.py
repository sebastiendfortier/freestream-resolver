#!/usr/bin/env python3
"""Verify movie resolve returns playable or scrape URL."""

from __future__ import annotations

import sys

from freestream_resolver.models import ScrapeRequest
from freestream_resolver.orchestrator import collect_candidates, resolve_request


def main() -> int:
    req = ScrapeRequest(
        imdb_id="tt0468569",
        title="The Dark Knight",
        year=2008,
        media_type="movie",
    )
    resolved = resolve_request(req, use_flare=False)
    if resolved:
        url = resolved[0].stream_url.lower()
        if any(ext in url for ext in (".m3u8", ".mp4", ".webm")) or "googlevideo" in url:
            print("RESOLVE_PLAYABLE_OK")
            return 0

    candidates = collect_candidates(req)
    if candidates:
        print("RESOLVE_PLAYABLE_OK")
        return 0

    print("RESOLVE_PLAYABLE_FAIL", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
