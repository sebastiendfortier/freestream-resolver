#!/bin/sh
set -e
cd "$(dirname "$0")/.."
pixi run python tools/fetch_kodi_plugins.py --verify | grep -q KODI_REPOS_OK
pixi run python tools/verify_plugin_manifest.py | grep -q PLUGIN_MANIFEST_OK
pixi run python tools/inventory_scrapers.py | grep -q SCRAPER_INVENTORY_OK
pixi run python tools/extract_free99_tmdb_key.py --verify | grep -q FREE99_TMDB_KEY_OK
pixi run python -m pytest tests/ -q
pixi run python scripts/verify_resolve_movie.py | grep -q RESOLVE_MOVIE
echo ALL_MET
