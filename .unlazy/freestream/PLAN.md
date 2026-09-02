# FreeStream orchestration plan

## Inventory

| ID | Outcome | Repo | State |
|----|---------|------|-------|
| leaf-resolver | Kodi fetch + inventory + resolver core | freestream-resolver | DONE |
| leaf-database | Catalog + web + MSI + stream_bridge | freestream-database | DONE |
| leaf-tv | APK + filter parity + ONN | freestream-tv | DONE |
| node-root | v0.1.0 shipped | .unlazy/freestream | DONE |
| v0.2-catalog | 1000+ titles + TV sync | freestream-database | DONE |
| v0.2-resolver | 3 scrapers + TV resolve | freestream-resolver | DONE |
| v0.2-tv | StreamResolver + ONN 0.2.0 | freestream-tv | DONE |
| v0.2-desktop | Windows MSI CI | freestream-database | DONE |
| node-v0.2 | Integration gates ALL MET | .unlazy/freestream/GATES-v0.2.md | DONE |

## Dependencies

- leaf-database Needs leaf-resolver (vendor + stream API)
- leaf-tv Needs leaf-database (catalog export)
- node-root Needs leaf-resolver, leaf-database, leaf-tv

## Ledgers

- `freestream-resolver/GATES.md`
- `freestream-database/GATES-local.md` (when created)
- `freestream-tv/GATES-local.md` (when created)
- `.unlazy/freestream/GATES.md` (integration)
