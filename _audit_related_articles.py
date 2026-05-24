"""Audit related-articles sections across all service hubs.

Prints, for each hub, the blog hrefs inside the #articles (related-articles) section.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

HUBS = [
    "deck-builder", "deck-railings", "fence-installation", "bathroom-renovation",
    "basement-renovation", "handyman-plumbing-services", "canopy",
    "landscaping-services", "general-contractor", "handyman-services",
    "interlocking-paver-services", "carpenter-services",
    "electrical-handyman-services", "handyman-painting-services",
    "demolition-services", "excavation-services", "home-renovation",
    "christmas-lights-installation-toronto-gta",
]

OPEN_RE = re.compile(
    r'<section[^>]*\b(?:id="articles"|class="[^"]*related-articles[^"]*")[^>]*>',
    re.I,
)


def extract_articles_block(html: str) -> str | None:
    m = OPEN_RE.search(html)
    if not m:
        return None
    section_open = re.compile(r"<section\b", re.I)
    section_close = re.compile(r"</section>", re.I)
    depth = 1
    pos = m.end()
    while pos < len(html):
        o = section_open.search(html, pos)
        c = section_close.search(html, pos)
        if c is None:
            break
        if o is not None and o.start() < c.start():
            depth += 1
            pos = o.end()
        else:
            depth -= 1
            pos = c.end()
            if depth == 0:
                return html[m.start():pos]
    return None


HREF_RE = re.compile(r'href="([^"]+)"', re.I)
H3_RE = re.compile(r'<h3[^>]*>(.*?)</h3>', re.I | re.S)


def main() -> None:
    for hub in HUBS:
        path = ROOT / hub / "index.html"
        if not path.exists():
            print(f"[skip] {hub}: missing index.html")
            continue
        html = path.read_text(encoding="utf-8")
        block = extract_articles_block(html)
        if block is None:
            print(f"[NONE] {hub}")
            continue
        # Extract anchor hrefs + titles
        cards = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, re.I | re.S)
        print(f"\n=== {hub} ({len(cards)} cards) ===")
        for href, inner in cards:
            title_m = H3_RE.search(inner)
            title = title_m.group(1).strip() if title_m else inner.strip()[:60]
            print(f"  {href}  ::  {title}")


if __name__ == "__main__":
    main()
