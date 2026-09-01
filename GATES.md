# Gates: freestream-resolver Phase 0–1

OWNS: tools/**, vendor/**, docs/**, src/freestream_resolver/**, tests/**, scripts/**, GATES.md

Scope: Kodi plugin acquisition, scraper inventory, resolver core, live scrape verification

- [x] G1: Repository zips fetched and manifest written
  CHECK: pixi run python tools/fetch_kodi_plugins.py --verify
  EXPECT: KODI_REPOS_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=KODI_REPOS_OK

- [x] G2: Plugin manifest lists required addon IDs
  CHECK: pixi run python tools/verify_plugin_manifest.py
  EXPECT: PLUGIN_MANIFEST_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=PLUGIN_MANIFEST_OK

- [x] G3: Scraper inventory generated from extracted zips
  CHECK: pixi run python tools/inventory_scrapers.py
  EXPECT: SCRAPER_INVENTORY_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=SCRAPER_INVENTORY_OK count=88

- [x] G4: Free99 TMDb API key extracted
  CHECK: pixi run python tools/extract_free99_tmdb_key.py --verify
  EXPECT: FREE99_TMDB_KEY_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=FREE99_TMDB_KEY_OK

- [x] G5: Resolver unit tests pass
  CHECK: pixi run python -m pytest tests/ -q
  EXPECT: passed
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=....                                                                     [100%] | 4 passed in 0.04s

- [x] G6: Movie scrape path verified
  CHECK: pixi run python scripts/verify_resolve_movie.py
  EXPECT: RESOLVE_MOVIE
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=RESOLVE_MOVIE_SCRAPE_OK
