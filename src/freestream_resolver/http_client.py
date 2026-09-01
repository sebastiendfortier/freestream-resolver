"""HTTP client with optional FlareSolverr bypass."""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_FLARESOLVERR = "http://127.0.0.1:8191/v1"
KODI_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def flaresolverr_url() -> str:
    return os.environ.get("FREESTREAM_FLARESOLVERR_URL", DEFAULT_FLARESOLVERR).rstrip("/")


def flaresolverr_enabled() -> bool:
    return os.environ.get("FREESTREAM_FLARESOLVERR_ENABLED", "1").lower() not in (
        "0",
        "false",
        "no",
    )


def solve_cloudflare(client: httpx.Client, url: str, timeout: float = 60.0) -> str | None:
    """Return HTML from FlareSolverr or None if unavailable."""
    if not flaresolverr_enabled():
        return None
    payload = {
        "cmd": "request.get",
        "url": url,
        "maxTimeout": int(timeout * 1000),
    }
    try:
        resp = client.post(flaresolverr_url(), json=payload, timeout=timeout + 10)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return None
    if data.get("status") != "ok":
        return None
    solution = data.get("solution") or {}
    return solution.get("response") or solution.get("html")


def get(
    client: httpx.Client,
    url: str,
    *,
    use_flare: bool = False,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    hdrs = {"User-Agent": KODI_UA}
    if headers:
        hdrs.update(headers)
    if use_flare:
        html = solve_cloudflare(client, url)
        if html:
            return httpx.Response(200, text=html, request=httpx.Request("GET", url))
    return client.get(url, headers=hdrs, follow_redirects=True)


def health_check(client: httpx.Client | None = None) -> dict[str, Any]:
    own = client is None
    if own:
        client = httpx.Client(timeout=10.0)
    try:
        resp = client.post(
            flaresolverr_url(),
            json={"cmd": "sessions.list"},
        )
        ok = resp.status_code == 200 and resp.json().get("status") == "ok"
        return {"ok": ok, "url": flaresolverr_url()}
    except Exception as exc:
        return {"ok": False, "url": flaresolverr_url(), "error": str(exc)}
    finally:
        if own:
            client.close()
