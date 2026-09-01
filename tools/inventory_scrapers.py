#!/usr/bin/env python3
"""Inventory scraper modules from vendored Kodi plugin zips."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor" / "kodi-repos"
PLUGINS = VENDOR / "plugins"
OUT = ROOT / "docs" / "scraper-inventory.md"
MANIFEST = VENDOR / "manifest.json"

SCRAPER_GLOB = "**/sources/working/*.py"


def resolve_addon_root(extract_dir: Path) -> Path:
    if (extract_dir / "addon.xml").is_file():
        return extract_dir
    for child in extract_dir.iterdir():
        if child.is_dir() and (child / "addon.xml").is_file():
            return child
    return extract_dir


def find_plugin_dir(addon_id: str) -> Path | None:
    if not PLUGINS.exists():
        return None
    for path in sorted(PLUGINS.glob(f"{addon_id}-*")):
        if path.is_dir():
            return resolve_addon_root(path)
    return None


def list_scrapers(plugin_root: Path) -> list[str]:
    working = plugin_root / "resources" / "lib" / "sources" / "working"
    if not working.is_dir():
        return []
    return sorted(
        p.stem
        for p in working.glob("*.py")
        if p.name != "__init__.py" and not p.name.startswith("_")
    )


def main() -> int:
    if not MANIFEST.exists():
        print("Run fetch_kodi_plugins.py first", file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    addon_ids = [
        "plugin.video.gratisred",
        "plugin.video.scrubsv2",
        "plugin.video.free99",
    ]

    sections: list[str] = ["# Scraper inventory\n", f"Generated from `{MANIFEST.relative_to(ROOT)}`.\n"]
    all_scrapers: dict[str, set[str]] = {}

    for addon_id in addon_ids:
        root = find_plugin_dir(addon_id)
        if root is None:
            print(f"Plugin not found: {addon_id}", file=sys.stderr)
            return 1
        scrapers = list_scrapers(root)
        all_scrapers[addon_id] = set(scrapers)
        ver = ""
        for repo in manifest["repos"].values():
            if addon_id in repo.get("plugins", {}):
                ver = repo["plugins"][addon_id]["version"]
                break
        sections.append(f"\n## {addon_id} v{ver}\n")
        sections.append(f"Path: `{root.relative_to(ROOT)}`\n")
        sections.append(f"**{len(scrapers)}** working scrapers:\n")
        for s in scrapers:
            sections.append(f"- `{s}`\n")

    # Overlap
    scrubsv2 = all_scrapers.get("plugin.video.scrubsv2", set())
    sections.append("\n## Overlap\n")
    for other in ("plugin.video.gratisred", "plugin.video.free99"):
        other_set = all_scrapers.get(other, set())
        shared = sorted(scrubsv2 & other_set)
        sections.append(f"\n### {other} ∩ scrubsv2 ({len(shared)})\n")
        for s in shared:
            sections.append(f"- `{s}`\n")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(sections), encoding="utf-8")
    print(f"SCRAPER_INVENTORY_OK count={sum(len(v) for v in all_scrapers.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
