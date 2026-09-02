# Gates: freestream-resolver v0.2

OWNS: src/freestream_resolver/**, scripts/**, GATES-v0.2.md

Scope: Multi-scraper orchestration, TV resolve path, FlareSolverr probe

- [x] G1: At least three scrapers registered
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-resolver && pixi run python scripts/verify_scraper_count.py'
  EXPECT: SCRAPER_COUNT_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=SCRAPER_COUNT_OK count=3

- [ ] G2: TV show scrape path returns candidates
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-resolver && pixi run python scripts/verify_resolve_tv.py'
  EXPECT: RESOLVE_TV
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=1; path=c2fddda5c8ee/25; out=Traceback (most recent call last): |   File "/home/slyfox/Documents/freestream-resolver/scripts/verify_resolve_tv.py", line 30, in <module> |     raise SystemExit(main()) |                      ~~~~^^ |   File "/home/slyfox/Documents/freest...

- [x] G3: FlareSolverr health probe (skip if daemon down)
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-resolver && pixi run python scripts/verify_flaresolverr_optional.py'
  EXPECT: FLARESOLVERR
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=FLARESOLVERR_SKIP
