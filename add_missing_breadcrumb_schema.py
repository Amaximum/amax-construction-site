#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent

TARGETS = [
    "deck-builder-gta/index.html",
    "deck-builder-schomberg/index.html",
    "deck-builder-toronto/index.html",
    "deck-contractor-bradford/index.html",
    "deck-contractor-burlington/index.html",
    "deck-contractor-hamilton/index.html",
    "deck-contractor-scarborough/index.html",
    "deck-contractor-woodbridge/index.html",
]


def strip_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_name(text: str) -> str:
    # Remove common title suffix and trim spaces.
    text = re.sub(r"\s*\|\s*aMaximum Construction\s*$", "", text)
    return text.strip()


def build_breadcrumb_schema(page_name: str, canonical: str) -> str:
    obj = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": "https://amaximumconstruction.com/",
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Services",
                "item": "https://amaximumconstruction.com/#services",
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": page_name,
                "item": canonical,
            },
        ],
    }
    payload = json.dumps(obj, ensure_ascii=True, separators=(",", ": "))
    return f'<script type="application/ld+json">\n{payload}\n</script>\n'


def process(path: Path) -> bool:
    src = path.read_text(encoding="utf-8")
    if re.search(r'"@type"\s*:\s*"BreadcrumbList"', src):
        return False

    canon_m = re.search(
        r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']\s*/?>',
        src,
        flags=re.IGNORECASE,
    )
    if not canon_m:
        return False
    canonical = canon_m.group(1)

    h1_m = re.search(r"<h1[^>]*>(.*?)</h1>", src, flags=re.IGNORECASE | re.DOTALL)
    title_m = re.search(r"<title>(.*?)</title>", src, flags=re.IGNORECASE | re.DOTALL)

    if h1_m:
        page_name = strip_tags(h1_m.group(1))
    elif title_m:
        page_name = normalize_name(strip_tags(title_m.group(1)))
    else:
        page_name = "Deck Service"

    schema = build_breadcrumb_schema(page_name, canonical)
    out = src.replace("</head>", schema + "</head>", 1)

    if out == src:
        return False

    path.write_text(out, encoding="utf-8")
    return True


def main() -> None:
    updated = 0
    for rel in TARGETS:
        path = ROOT / rel
        if not path.exists():
            print(f"[miss] {rel}")
            continue
        if process(path):
            updated += 1
            print(f"[ok]   {rel}")
        else:
            print(f"[skip] {rel}")
    print(f"Done. {updated}/{len(TARGETS)} updated.")


if __name__ == "__main__":
    main()
