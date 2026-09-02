# Gates: FreeStream v0.3 integration

OWNS: .unlazy/freestream/**

Scope: All v0.3 leaf gates met including MSI CI

- [x] G1: freestream-database v0.3 gates met
  CHECK: /bin/sh /home/slyfox/Documents/freestream-database/scripts/verify_v0.3_gates.sh
  EXPECT: ALL_MET
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-database; exit=0; path=00db6cba9506/22; out=..                                                                       [100%] | =============================== warnings summary =============================== | .pixi/envs/default/lib/python3.14/site-packages/fastapi/testclient.py:1 |  ...

- [x] G2: freestream-resolver v0.3 gates met
  CHECK: /bin/sh /home/slyfox/Documents/freestream-resolver/scripts/verify_v0.3_gates.sh
  EXPECT: ALL_MET
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-database; exit=0; path=00db6cba9506/22; out=....                                                                     [100%] | 4 passed in 0.04s | ALL_MET

- [x] G3: freestream-tv v0.3 gates met
  CHECK: /bin/sh /home/slyfox/Documents/freestream-tv/scripts/verify_v0.3_gates.sh
  EXPECT: ALL_MET
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-database; exit=0; path=00db6cba9506/22; out=ALL_MET

- [x] G4: MSI CI verified
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_msi_ci.py'
  EXPECT: MSI_CI_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-database; exit=0; path=00db6cba9506/22; out=MSI_CI_OK
