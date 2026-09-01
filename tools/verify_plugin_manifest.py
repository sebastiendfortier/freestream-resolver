#!/usr/bin/env python3
"""Verify vendor/kodi-repos/manifest.json lists required plugins."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "vendor" / "kodi-repos" / "manifest.json"

REQUIRED = [
    "plugin.video.gratisred",
    "plugin.video.scrubsv2",
    "plugin.video.free99",
]


def main() -> int:
    if not MANIFEST.exists():
        print("manifest.json missing", file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    found: set[str] = set()
    for repo in manifest.get("repos", {}).values():
        found.update(repo.get("plugins", {}).keys())

    missing = [p for p in REQUIRED if p not in found]
    if missing:
        print(f"Missing: {missing}", file=sys.stderr)
        return 1

    for addon_id in REQUIRED:
        ok = False
        for repo in manifest["repos"].values():
            info = repo.get("plugins", {}).get(addon_id)
            if info and (ROOT / info["extracted"]).is_dir():
                ok = True
                break
        if not ok:
            print(f"Not extracted: {addon_id}", file=sys.stderr)
            return 1

    print("PLUGIN_MANIFEST_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
