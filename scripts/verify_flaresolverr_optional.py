#!/usr/bin/env python3
"""FlareSolverr probe — OK if running, SKIP if not (dev hosts without Docker)."""

from __future__ import annotations

import sys

from freestream_resolver.http_client import health_check


def main() -> int:
    result = health_check()
    if result.get("ok"):
        print("FLARESOLVERR_OK")
        return 0
    print("FLARESOLVERR_SKIP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
