#!/bin/sh
set -e
cd "$(dirname "$0")/.."
pixi run python scripts/verify_scraper_count.py --min 6 | grep -q SCRAPER_COUNT_OK
pixi run python scripts/verify_resolve_tv.py | grep -q RESOLVE_TV
pixi run python scripts/verify_resolve_playable.py | grep -q RESOLVE_PLAYABLE_OK
pixi run python -m pytest tests/ -q
echo ALL_MET
