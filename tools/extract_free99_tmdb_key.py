#!/usr/bin/env python3
"""Extract default TMDb API key from vendored plugin.video.free99."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "vendor" / "kodi-repos" / "plugins"
OUT = ROOT / "config" / "tmdb.json"

KEY_PATTERNS = [
    re.compile(r"API_KEY\s*=\s*['\"]([a-f0-9]{32})['\"]", re.I),
    re.compile(r'tmdb\.apikey["\']?\s*,\s*["\']([a-f0-9]{32})["\']', re.I),
    re.compile(r'apikey["\']?\s*[=:]\s*["\']([a-f0-9]{32})["\']', re.I),
    re.compile(r'api_key["\']?\s*[=:]\s*["\']([a-f0-9]{32})["\']', re.I),
    re.compile(r'default=["\']([a-f0-9]{32})["\']', re.I),
]


def resolve_addon_root(extract_dir: Path) -> Path:
    if (extract_dir / "addon.xml").is_file():
        return extract_dir
    for child in extract_dir.iterdir():
        if child.is_dir() and (child / "addon.xml").is_file():
            return child
    return extract_dir


def find_free99_root() -> Path | None:
    for path in sorted(PLUGINS.glob("plugin.video.free99-*")):
        if path.is_dir():
            return resolve_addon_root(path)
    return None


def search_key_in_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    for pat in KEY_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1)
    return None


def extract_key(root: Path) -> str | None:
    candidates = [
        root / "resources" / "settings.xml",
        root / "resources" / "lib" / "modules" / "tmdb_utils.py",
        root / "resources" / "lib" / "modules" / "tmdb.py",
    ]
    for path in candidates:
        key = search_key_in_file(path)
        if key:
            return key
    # Walk modules for any tmdb file
    modules = root / "resources" / "lib" / "modules"
    if modules.is_dir():
        for py in modules.rglob("*.py"):
            key = search_key_in_file(py)
            if key:
                return key
    return None


def write_config(key: str, root: Path) -> None:
    ver = root.name.replace("plugin.video.free99-", "")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "api_key": key,
                "base_url": "https://api.themoviedb.org/3/",
                "source_addon": "plugin.video.free99",
                "source_version": ver,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.verify and OUT.exists():
        data = json.loads(OUT.read_text(encoding="utf-8"))
        key = data.get("api_key", "")
        if len(key) == 32 and key.isalnum():
            print("FREE99_TMDB_KEY_OK")
            return 0
        print("Invalid cached key", file=sys.stderr)
        return 1

    root = find_free99_root()
    if root is None:
        print("plugin.video.free99 not vendored", file=sys.stderr)
        return 1

    key = extract_key(root)
    if not key:
        print("TMDb key not found in free99 plugin", file=sys.stderr)
        return 1

    write_config(key, root)
    print("FREE99_TMDB_KEY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
