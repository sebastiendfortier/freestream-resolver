"""Resolve hoster URLs to playable streams."""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any

import httpx

from freestream_resolver.embed_chain import extract_media_urls, prepare_link
from freestream_resolver.http_client import KODI_UA, get
from freestream_resolver.models import ResolvedStream, StreamCandidate


def _yt_dlp_resolve(url: str) -> ResolvedStream | None:
    exe = shutil.which("yt-dlp") or shutil.which("youtube-dl")
    if not exe:
        return None
    try:
        proc = subprocess.run(
            [exe, "-g", "--no-warnings", url],
            capture_output=True,
            text=True,
            timeout=90,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return None
        stream_url = proc.stdout.strip().splitlines()[0]
        return ResolvedStream(
            stream_url=stream_url,
            quality="HD",
            headers={"User-Agent": KODI_UA, "Referer": url},
            provider="yt-dlp",
            source_url=url,
        )
    except Exception:
        return None


def _direct_resolve(url: str, referer: str = "") -> ResolvedStream | None:
    lower = url.lower()
    if any(ext in lower for ext in (".m3u8", ".mp4", ".webm")):
        headers = {"User-Agent": KODI_UA}
        if referer:
            headers["Referer"] = referer
        if "|User-Agent=" in url:
            base, _, tail = url.partition("|")
            stream_url = base
            if "Referer=" in tail:
                ref = tail.split("Referer=", 1)[-1]
                headers["Referer"] = ref
            return ResolvedStream(stream_url=stream_url, quality="HD", headers=headers, provider="direct", source_url=url)
        return ResolvedStream(stream_url=url, quality="HD", headers=headers, provider="direct", source_url=url)
    return None


def resolve_candidate(
    client: httpx.Client,
    candidate: StreamCandidate,
    *,
    use_flare: bool = False,
) -> ResolvedStream | None:
    url = prepare_link(candidate.url) or candidate.url
    direct = _direct_resolve(url)
    if direct:
        return direct

    try:
        resp = get(client, url, use_flare=use_flare)
        for media in extract_media_urls(resp.text):
            d = _direct_resolve(media, referer=url)
            if d:
                return d
    except Exception:
        pass

    return _yt_dlp_resolve(url)


def resolve_all(
    client: httpx.Client,
    candidates: list[StreamCandidate],
    *,
    use_flare: bool = False,
    limit: int = 5,
) -> list[ResolvedStream]:
    out: list[ResolvedStream] = []
    seen: set[str] = set()
    for cand in candidates:
        if len(out) >= limit:
            break
        resolved = resolve_candidate(client, cand, use_flare=use_flare)
        if resolved and resolved.stream_url not in seen:
            seen.add(resolved.stream_url)
            out.append(resolved)
    return out
