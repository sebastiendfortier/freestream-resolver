#!/usr/bin/env python3
"""Verify orchestrator registers at least three scrapers."""

from __future__ import annotations

import sys

from freestream_resolver.orchestrator import SCRAPERS


def main() -> int:
    if len(SCRAPERS) < 3:
        print(f"SCRAPER_COUNT_LOW count={len(SCRAPERS)}", file=sys.stderr)
        return 1
    print(f"SCRAPER_COUNT_OK count={len(SCRAPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
