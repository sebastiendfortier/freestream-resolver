#!/usr/bin/env python3
"""Download Kodi repository zips and extract target video plugins (mirrors Kodi install)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor" / "kodi-repos"
MANIFEST_PATH = VENDOR / "manifest.json"

KODI_UA = "Kodi/21.0 (Linux; Android 11.0; SM-G991B Build/RP1A.200720.012)"

REQUIRED_PLUGINS = [
    "plugin.video.gratisred",
    "plugin.video.scrubsv2",
    "plugin.video.free99",
]

OPTIONAL_PLUGINS = [
    "script.module.resolveurl",
]

REPO_SOURCES = [
    {
        "name": "redwizard",
        "repo_zip": "https://repo.redwizard.xyz/repository.redwizard-1.2.2.zip",
        "addons_xml": "https://repo.redwizard.xyz/redwizardrepo/main/addons.xml",
        "datadir": "https://repo.redwizard.xyz/redwizardrepo/main/",
        "targets": ["plugin.video.gratisred"],
    },
    {
        "name": "jewrepo",
        "repo_zip": "https://jewbmx.github.io/repository.jewrepo-1.6.0.zip",
        "addons_xml": "https://raw.githubusercontent.com/jewbmx/repo/master/addons.xml",
        "datadir": "https://raw.githubusercontent.com/jewbmx/repo/master/zips/",
        "targets": ["plugin.video.scrubsv2"],
        "subdir_repo": "https://raw.githubusercontent.com/Gujal00/smrzips/master/addons.xml",
        "subdir_datadir": "https://raw.githubusercontent.com/Gujal00/smrzips/master/zips/",
        "subdir_targets": ["script.module.resolveurl"],
    },
    {
        "name": "diggz",
        "repo_zip": "https://nebulous42069.github.io/diggz/Diggz_Repo.zip",
        "addons_xml": "https://raw.githubusercontent.com/nebulous42069/Omega/main/omega/zips/addons.xml",
        "datadir": "https://raw.githubusercontent.com/nebulous42069/Omega/main/omega/zips/",
        "targets": ["plugin.video.free99"],
    },
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_bytes(client: httpx.Client, url: str) -> bytes:
    resp = client.get(url, follow_redirects=True)
    resp.raise_for_status()
    return resp.content


def parse_addon_versions(addons_xml: str) -> dict[str, str]:
    """Return addon_id -> version from addons.xml."""
    versions: dict[str, str] = {}
    try:
        root = ET.fromstring(addons_xml)
    except ET.ParseError:
        # Fallback regex for malformed XML
        for match in re.finditer(
            r'<addon[^>]+id="([^"]+)"[^>]+version="([^"]+)"', addons_xml
        ):
            aid, ver = match.group(1), match.group(2)
            versions[aid] = ver
        return versions

    for addon in root.iter("addon"):
        aid = addon.attrib.get("id")
        ver = addon.attrib.get("version")
        if aid and ver:
            versions[aid] = ver
    return versions


def zip_url_for_addon(datadir: str, addon_id: str, version: str) -> list[str]:
    """Candidate zip URLs (Kodi repos use several layouts)."""
    base = datadir if datadir.endswith("/") else datadir + "/"
    name = f"{addon_id}-{version}.zip"
    candidates = [
        urljoin(base, name),
        urljoin(base, f"{addon_id}/{name}"),
        urljoin(base, f"{addon_id.replace('.', '_')}/{name}"),
    ]
    return candidates


def download_plugin_zip(
    client: httpx.Client, datadir: str, addon_id: str, version: str, dest: Path
) -> str:
    last_err: Exception | None = None
    for url in zip_url_for_addon(datadir, addon_id, version):
        try:
            data = fetch_bytes(client, url)
            if len(data) < 1000:
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            return url
        except Exception as exc:
            last_err = exc
    raise RuntimeError(f"Could not download {addon_id}-{version}: {last_err}")


def extract_zip(zip_path: Path, dest_dir: Path) -> None:
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)


def process_source(client: httpx.Client, source: dict, manifest: dict) -> None:
    name = source["name"]
    repos_dir = VENDOR / "repos"
    repos_dir.mkdir(parents=True, exist_ok=True)

    repo_zip_path = repos_dir / f"repository.{name}.zip"
    print(f"Fetching repo zip: {source['repo_zip']}")
    repo_zip_path.write_bytes(fetch_bytes(client, source["repo_zip"]))

    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(repo_zip_path, "r") as zf:
            zf.extractall(tmp)

    addons_xml_text = fetch_bytes(client, source["addons_xml"]).decode("utf-8", errors="replace")
    versions = parse_addon_versions(addons_xml_text)

    manifest["repos"][name] = {
        "repo_zip": source["repo_zip"],
        "repo_zip_sha256": sha256_file(repo_zip_path),
        "addons_xml": source["addons_xml"],
        "plugins": {},
    }

    all_targets = list(source.get("targets", []))
    datadir = source["datadir"]

    if source.get("subdir_repo"):
        sub_xml = fetch_bytes(client, source["subdir_repo"]).decode("utf-8", errors="replace")
        sub_versions = parse_addon_versions(sub_xml)
        versions.update(sub_versions)
        all_targets.extend(source.get("subdir_targets", []))
        # subdir targets use subdir datadir
        sub_datadir = source.get("subdir_datadir", datadir)

    plugins_dir = VENDOR / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)

    for addon_id in all_targets:
        version = versions.get(addon_id)
        if not version:
            print(f"WARNING: {addon_id} not found in addons.xml for {name}", file=sys.stderr)
            continue

        use_datadir = (
            source.get("subdir_datadir", datadir)
            if addon_id in source.get("subdir_targets", [])
            else datadir
        )

        zip_dest = plugins_dir / f"{addon_id}-{version}.zip"
        url = download_plugin_zip(client, use_datadir, addon_id, version, zip_dest)
        extract_dest = plugins_dir / f"{addon_id}-{version}"
        extract_zip(zip_dest, extract_dest)

        manifest["repos"][name]["plugins"][addon_id] = {
            "version": version,
            "zip_url": url,
            "zip_sha256": sha256_file(zip_dest),
            "extracted": str(extract_dest.relative_to(ROOT)),
        }
        print(f"OK {addon_id} v{version}")


def fetch_all() -> dict:
    VENDOR.mkdir(parents=True, exist_ok=True)
    manifest: dict = {"repos": {}, "required_plugins": REQUIRED_PLUGINS}

    headers = {"User-Agent": KODI_UA, "Accept": "*/*", "Referer": "https://repo.redwizard.xyz/"}
    with httpx.Client(timeout=120.0, headers=headers) as client:
        for source in REPO_SOURCES:
            process_source(client, source, manifest)

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def verify(manifest: dict | None = None) -> bool:
    if manifest is None:
        if not MANIFEST_PATH.exists():
            print("manifest.json missing", file=sys.stderr)
            return False
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    found: set[str] = set()
    for repo in manifest.get("repos", {}).values():
        found.update(repo.get("plugins", {}).keys())

    missing = [p for p in REQUIRED_PLUGINS if p not in found]
    if missing:
        print(f"Missing plugins: {missing}", file=sys.stderr)
        return False

    for addon_id in REQUIRED_PLUGINS:
        for repo in manifest["repos"].values():
            info = repo.get("plugins", {}).get(addon_id)
            if info:
                extract_path = ROOT / info["extracted"]
                if not extract_path.is_dir():
                    print(f"Extract missing: {extract_path}", file=sys.stderr)
                    return False

    print("KODI_REPOS_OK")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help="Verify manifest only")
    args = parser.parse_args()

    if args.verify:
        return 0 if verify() else 1

    manifest = fetch_all()
    if not verify(manifest):
        return 1
    print("KODI_REPOS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
