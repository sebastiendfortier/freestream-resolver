#!/usr/bin/env python3
"""CLI for FreeStream resolver."""

from __future__ import annotations

import argparse
import json
import sys

from freestream_resolver.models import ScrapeRequest
from freestream_resolver.orchestrator import resolve_request


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FreeStream resolver")
    parser.add_argument("--imdb", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--type", choices=["movie", "tv"], default="movie")
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument("--season", type=int, default=None)
    parser.add_argument("--episode", type=int, default=None)
    parser.add_argument("--flare", action="store_true")
    args = parser.parse_args(argv)

    req = ScrapeRequest(
        imdb_id=args.imdb,
        title=args.title,
        year=args.year,
        media_type=args.type,
        season=args.season,
        episode=args.episode,
    )
    streams = resolve_request(req, use_flare=args.flare)
    if not streams:
        print("NO_STREAMS", file=sys.stderr)
        return 1
    print(json.dumps([s.__dict__ for s in streams], indent=2))
    print("RESOLVE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
