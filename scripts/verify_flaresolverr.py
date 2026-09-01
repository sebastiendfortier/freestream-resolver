"""Test FlareSolverr health — used by verify_flaresolverr gate."""

from __future__ import annotations

import sys

from freestream_resolver.http_client import health_check


def main() -> int:
    result = health_check()
    if result.get("ok"):
        print("FLARESOLVERR_OK")
        return 0
    print(f"FlareSolverr unavailable: {result}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
