#!/bin/sh
set -e
cd "$(dirname "$0")/.."
pixi run python scripts/verify_scraper_count.py | grep -q SCRAPER_COUNT_OK
pixi run python scripts/verify_resolve_tv.py | grep -q RESOLVE_TV
pixi run python scripts/verify_flaresolverr_optional.py | grep -q FLARESOLVERR
echo ALL_MET
