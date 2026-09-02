# Gates: FreeStream v0.3 integration

OWNS: .unlazy/freestream/**

Scope: All v0.3 leaf gates met including MSI CI

- [ ] G1: freestream-database v0.3 gates met
  CHECK: /bin/sh /home/slyfox/Documents/freestream-database/scripts/verify_v0.3_gates.sh
  EXPECT: ALL_MET
  EVIDENCE: pending

- [ ] G2: freestream-resolver v0.3 gates met
  CHECK: /bin/sh /home/slyfox/Documents/freestream-resolver/scripts/verify_v0.3_gates.sh
  EXPECT: ALL_MET
  EVIDENCE: pending

- [ ] G3: freestream-tv v0.3 gates met
  CHECK: /bin/sh /home/slyfox/Documents/freestream-tv/scripts/verify_v0.3_gates.sh
  EXPECT: ALL_MET
  EVIDENCE: pending

- [ ] G4: MSI CI verified
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_msi_ci.py'
  EXPECT: MSI_CI_OK
  EVIDENCE: pending
