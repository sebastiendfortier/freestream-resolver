"""HTML parsing helpers (Scrubs client_utils.parseDOM subset)."""

from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup


def parse_dom(html: str, tag: str, attrs: dict[str, str] | None = None, ret: str | None = None) -> list[Any]:
    soup = BeautifulSoup(html or "", "lxml")
    kwargs: dict[str, str] = {}
    if attrs:
        for k, v in attrs.items():
            if k == "class":
                kwargs["class_"] = v
            else:
                kwargs[k] = v
    nodes = soup.find_all(tag, **kwargs)
    if ret == "href":
        return [n.get("href", "") for n in nodes if n.get("href")]
    if ret:
        return [n.get(ret, "") for n in nodes]
    return [str(n) for n in nodes]


def remove_tags(html: str) -> str:
    return BeautifulSoup(html or "", "lxml").get_text(" ", strip=True)


def clean_title(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text or "")
    return re.sub(r"\s+", " ", text).strip().lower()
