# Gates: FreeStream integration (root)

OWNS: .unlazy/freestream/**

Scope: All leaf repos verified locally and ONN deploy complete

- [x] G1: freestream-resolver gates met
  CHECK: /bin/sh /home/slyfox/Documents/freestream-resolver/scripts/verify_all_local_gates.sh
  EXPECT: ALL_MET
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=....                                                                     [100%] | 4 passed in 0.05s | ALL_MET

- [x] G2: freestream-database local gates met
  CHECK: /bin/sh /home/slyfox/Documents/freestream-database/scripts/verify_all_local_gates.sh
  EXPECT: ALL_MET
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=..                                                                       [100%] | =============================== warnings summary =============================== | .pixi/envs/default/lib/python3.14/site-packages/fastapi/testclient.py:1 |  ...

- [x] G3: freestream-tv local gates met
  CHECK: /bin/sh /home/slyfox/Documents/freestream-tv/scripts/verify_all_local_gates.sh
  EXPECT: ALL_MET
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=ALL_MET

- [x] G4: ONN deploy gates met
  CHECK: /bin/sh /home/slyfox/Documents/freestream-tv/scripts/verify_onn_gates.sh
  EXPECT: ALL_MET
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=ALL_MET
