# FreeStream orchestration plan

## Inventory

| ID | Outcome | Repo | State |
|----|---------|------|-------|
| leaf-resolver | Kodi fetch + inventory + resolver core | freestream-resolver | IN-FLIGHT |
| leaf-database | Catalog + web + MSI + stream_bridge | freestream-database | WAITING |
| leaf-tv | APK + filter parity + ONN | freestream-tv | WAITING |
| node-root | Local gates ALL MET → ONN → push | .unlazy/freestream | OPEN |

## Dependencies

- leaf-database Needs leaf-resolver (vendor + stream API)
- leaf-tv Needs leaf-database (catalog export)
- node-root Needs leaf-resolver, leaf-database, leaf-tv

## Ledgers

- `freestream-resolver/GATES.md`
- `freestream-database/GATES-local.md` (when created)
- `freestream-tv/GATES-local.md` (when created)
- `.unlazy/freestream/GATES.md` (integration)
