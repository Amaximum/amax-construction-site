#!/usr/bin/env python3
"""Scan HTML/CSS for local asset references and report missing files.

Checks:
- <img src>, <source src/srcset>, <link rel=icon|apple-touch-icon|manifest href>
- CSS url(...) in *.css

Skips external URLs (http/https/data/mailto/tel).
"""

from __future__ import annotations

import re
from pathlib import Path
from html.parser import HTMLParser
from collections import defaultdict

ROOT = Path(r"c:\Users\maxim\Desktop\amax-Construction-site")

EXTERNAL_PREFIXES = (
    "http://",
    "https://",
    "data:",
    "mailto:",
    "tel:",
    "//",
)


def is_local_url(url: str) -> bool:
    url = (url or "").strip()
    if not url:
        return False
    if url.startswith(EXTERNAL_PREFIXES):
        return False
    if url.startswith("#"):
        return False
    return True


def url_to_path(url: str, base_dir: Path) -> Path | None:
    url = url.strip().split("#")[0].split("?")[0]
    if not url:
        return None
    if url.startswith("/"):
        return ROOT / url.lstrip("/")
    return (base_dir / url).resolve()


class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs_d = {k: v for k, v in attrs}

        if tag == "img" and attrs_d.get("src"):
            self.assets.append(attrs_d["src"])

        if tag == "source":
            if attrs_d.get("src"):
                self.assets.append(attrs_d["src"])
            if attrs_d.get("srcset"):
                self.assets.extend([s.strip().split()[0] for s in attrs_d["srcset"].split(",") if s.strip()])

        if tag == "link":
            rel = (attrs_d.get("rel") or "").lower()
            href = attrs_d.get("href")
            if href and any(x in rel for x in ("icon", "manifest", "apple-touch-icon")):
                self.assets.append(href)


CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)


def scan_html():
    missing: dict[str, list[str]] = defaultdict(list)
    for html_file in ROOT.rglob("*.html"):
        rel = str(html_file.relative_to(ROOT))
        base_dir = html_file.parent
        try:
            content = html_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        parser = AssetParser()
        parser.feed(content)

        for asset in parser.assets:
            if not is_local_url(asset):
                continue
            p = url_to_path(asset, base_dir)
            if p is None:
                continue
            if not p.exists():
                missing[str(p.relative_to(ROOT))].append(rel)

    return missing


def scan_css():
    missing: dict[str, list[str]] = defaultdict(list)
    for css_file in ROOT.rglob("*.css"):
        rel = str(css_file.relative_to(ROOT))
        base_dir = css_file.parent
        try:
            content = css_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        for _, url in CSS_URL_RE.findall(content):
            if not is_local_url(url):
                continue
            p = url_to_path(url, base_dir)
            if p is None:
                continue
            if not p.exists():
                missing[str(p.relative_to(ROOT))].append(rel)

    return missing


def main():
    html_missing = scan_html()
    css_missing = scan_css()

    total_missing = len(html_missing) + len(css_missing)
    print(f"Asset scan under {ROOT}")
    print(f"Missing unique assets: {total_missing}")

    if total_missing == 0:
        return

    if html_missing:
        print("\nMissing assets referenced from HTML:")
        for asset, pages in sorted(html_missing.items(), key=lambda x: -len(x[1])):
            print(f"- {asset}  (referenced on {len(pages)} page(s))")
            for p in pages[:8]:
                print(f"    {p}")
            if len(pages) > 8:
                print(f"    ... and {len(pages)-8} more")

    if css_missing:
        print("\nMissing assets referenced from CSS:")
        for asset, files in sorted(css_missing.items(), key=lambda x: -len(x[1])):
            print(f"- {asset}  (referenced in {len(files)} file(s))")
            for f in files[:8]:
                print(f"    {f}")
            if len(files) > 8:
                print(f"    ... and {len(files)-8} more")


if __name__ == "__main__":
    main()
