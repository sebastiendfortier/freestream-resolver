# FreeStream

MalStream-style movies/TV stack: TMDb catalog, Scrubs-lineage resolver, Android TV app.

## Repos

| Repo | Role |
|------|------|
| [freestream-resolver](https://github.com/sebastiendfortier/freestream-resolver) | Kodi plugin scrapers + hoster resolve |
| [freestream-database](https://github.com/sebastiendfortier/freestream-database) | Catalog API, web UI, Windows MSI |
| [freestream-tv](https://github.com/sebastiendfortier/freestream-tv) | Android TV client |

## Quick start

```bash
# Catalog web UI
cd freestream-database && pixi run serve

# Sync TV catalog assets
cd freestream-tv && pixi run sync-catalog

# Resolve a title
cd freestream-resolver && pixi run python -m freestream_resolver.cli \
  --imdb tt0468569 --title "The Dark Knight" --year 2008
```

FlareSolverr (optional): `docker run -d -p 8191:8191 ghcr.io/flaresolverr/flaresolverr:latest`
