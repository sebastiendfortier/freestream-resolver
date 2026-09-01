"""Embed chain normalization (subset of Scrubs scrape_sources.prepare_link)."""

from __future__ import annotations

import re
from urllib.parse import urlparse

DOOD_REDIRECT = {"dood.to", "dood.so", "dood.cx", "dood.pm", "ds2play.com", "doods.pro"}


def prepare_link(url: str) -> str | None:
    if not url:
        return None
    url = url.replace("\\/", "/").replace("\\", "").replace("///", "//")
    if url.startswith("//"):
        url = "https:" + url
    if not url.startswith("http"):
        url = re.sub(r"\s+", "", url)
    if not url.startswith("http"):
        return None
    u = url.replace("//www.", "//")
    try:
        host = urlparse(u).netloc.lower()
    except Exception:
        return url
    if host in DOOD_REDIRECT:
        return url.replace(host, "doodstream.com")
    return url


def extract_media_urls(html: str) -> list[str]:
    """Find direct m3u8/mp4 and common embed file patterns in HTML."""
    if not html:
        return []
    patterns = [
        r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)',
        r'(https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*)',
        r'file:\s*["\'](https?://[^"\']+)["\']',
        r'src:\s*["\'](https?://[^"\']+)["\']',
    ]
    found: list[str] = []
    for pat in patterns:
        for m in re.finditer(pat, html, re.I):
            u = m.group(1).rstrip("\\")
            if u not in found:
                found.append(u)
    return found
