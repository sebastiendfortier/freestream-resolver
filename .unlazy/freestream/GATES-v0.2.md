# Gates: FreeStream v0.2 integration

OWNS: .unlazy/freestream/**

Scope: Catalog scale, resolver depth, TV stream API, desktop CI

- [x] G1: freestream-database v0.2 catalog gates met
  CHECK: /bin/sh /home/slyfox/Documents/freestream-database/scripts/verify_v0.2_gates.sh
  EXPECT: ALL_MET
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/nixtoons resolver; exit=0; path=c2fddda5c8ee/25; out=CATALOG_ALREADY_OK rows=3971 | ALL_MET

- [x] G2: freestream-resolver v0.2 gates met
  CHECK: /bin/sh /home/slyfox/Documents/freestream-resolver/scripts/verify_v0.2_gates.sh
  EXPECT: ALL_MET
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/nixtoons resolver; exit=0; path=c2fddda5c8ee/25; out=ALL_MET

- [x] G3: freestream-tv v0.2 gates met
  CHECK: /bin/sh /home/slyfox/Documents/freestream-tv/scripts/verify_v0.2_gates.sh
  EXPECT: ALL_MET
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/nixtoons resolver; exit=0; path=c2fddda5c8ee/25; out=ALL_MET

- [x] G4: Windows MSI CI workflow present
  CHECK: /bin/sh -c 'test -f /home/slyfox/Documents/freestream-database/.github/workflows/build-windows.yml && python3 -c "import pathlib; t=pathlib.Path(\"/home/slyfox/Documents/freestream-database/.github/workflows/build-windows.yml\").read_text(); assert \"pyappdist\" in t; print(\"WINDOWS_CI_OK\")"'
  EXPECT: WINDOWS_CI_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/nixtoons resolver; exit=0; path=c2fddda5c8ee/25; out=WINDOWS_CI_OK
