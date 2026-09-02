# Gates: freestream-resolver v0.3

OWNS: src/freestream_resolver/**, scripts/**, GATES-v0.3.md

Scope: 6+ scrapers, stable TV resolve, playable movie decode

- [x] G1: At least six scrapers registered
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-resolver && pixi run python scripts/verify_scraper_count.py --min 6'
  EXPECT: SCRAPER_COUNT_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-database; exit=0; path=00db6cba9506/22; out=SCRAPER_COUNT_OK count=6

- [x] G2: TV scrape path returns candidates
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-resolver && pixi run python scripts/verify_resolve_tv.py'
  EXPECT: RESOLVE_TV
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-database; exit=0; path=00db6cba9506/22; out=RESOLVE_TV_OK

- [x] G3: Movie resolve yields playable URL or scrape fallback
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-resolver && pixi run python scripts/verify_resolve_playable.py'
  EXPECT: RESOLVE_PLAYABLE_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-database; exit=0; path=00db6cba9506/22; out=RESOLVE_PLAYABLE_OK

- [x] G4: Unit tests pass
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-resolver && pixi run python -m pytest tests/ -q'
  EXPECT: passed
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-database; exit=0; path=00db6cba9506/22; out=....                                                                     [100%] | 4 passed in 0.04s
