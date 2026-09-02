#!/usr/bin/env python3
"""Verify orchestrator registers minimum scraper count."""

from __future__ import annotations

import argparse
import sys

from freestream_resolver.orchestrator import SCRAPERS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min", type=int, default=3)
    args = parser.parse_args()
    if len(SCRAPERS) < args.min:
        print(f"SCRAPER_COUNT_LOW count={len(SCRAPERS)} need>={args.min}", file=sys.stderr)
        return 1
    print(f"SCRAPER_COUNT_OK count={len(SCRAPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
