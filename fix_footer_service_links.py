"""Sitewide footer fix: every service in the footer must point to its hub.

Some pages have stale footer hrefs pointing to terminal/location pages (e.g.
`/general-contractor-services-near-me/` instead of `/general-contractor/`).
This script scans every <footer>...</footer> on every HTML page and rewrites
service-row hrefs based on the visible anchor text.

Idempotent. Run from repo root:

    python fix_footer_service_links.py
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Canonical anchor-text -> hub URL.
# Keys are lowercased + ampersand-decoded + whitespace-collapsed.
TEXT_TO_HUB: dict[str, str] = {
    "deck building":            "/deck-builder/",
    "deck builder":             "/deck-builder/",
    "deck builders":            "/deck-builder/",
    "deck railings":            "/deck-railings/",
    "deck railing":             "/deck-railings/",
    "fence installation":       "/fence-installation/",
    "fence installer":          "/fence-installation/",
    "fencing":                  "/fence-installation/",
    "bathroom renovation":      "/bathroom-renovation/",
    "bathroom renovations":     "/bathroom-renovation/",
    "basement renovation":      "/basement-renovation/",
    "basement renovations":     "/basement-renovation/",
    "plumbing":                 "/handyman-plumbing-services/",
    "plumbing services":        "/handyman-plumbing-services/",
    "electrical":               "/electrical-handyman-services/",
    "electrical services":      "/electrical-handyman-services/",
    "painting":                 "/handyman-painting-services/",
    "painting services":        "/handyman-painting-services/",
    "canopy":                   "/canopy/",
    "canopy & awnings":         "/canopy/",
    "canopy and awnings":       "/canopy/",
    "canopies":                 "/canopy/",
    "landscaping":              "/landscaping-services/",
    "landscaping services":     "/landscaping-services/",
    "handyman":                 "/handyman-services/",
    "handyman services":        "/handyman-services/",
    "general contractor":       "/general-contractor/",
    "general contracting":      "/general-contractor/",
    "interlocking":             "/interlocking-paver-services/",
    "interlocking & paving":    "/interlocking-paver-services/",
    "interlocking and paving":  "/interlocking-paver-services/",
    "interlock":                "/interlocking-paver-services/",
    "paving":                   "/interlocking-paver-services/",
    "carpentry":                "/carpenter-services/",
    "carpenter":                "/carpenter-services/",
    "carpenter services":       "/carpenter-services/",
    "demolition":               "/demolition-services/",
    "demolition services":      "/demolition-services/",
    "excavation":               "/excavation-services/",
    "excavation services":      "/excavation-services/",
    "home renovation":          "/home-renovation/",
    "home renovations":         "/home-renovation/",
    "christmas lights":         "/christmas-lights-installation-toronto-gta/",
    "christmas light installation": "/christmas-lights-installation-toronto-gta/",
}


def normalize(text: str) -> str:
    """Lowercase, decode &amp;, collapse whitespace, strip arrows/punctuation."""
    t = re.sub(r"<[^>]+>", " ", text)
    t = t.replace("&amp;", "&").replace("&rarr;", "").replace("→", "")
    t = t.lower().strip()
    t = re.sub(r"\s+", " ", t)
    # Strip trailing punctuation
    t = t.strip(" .,:;-—")
    return t


FOOTER_RE = re.compile(r"<footer\b.*?</footer>", re.I | re.S)
LI_A_RE = re.compile(
    r'(<li[^>]*>\s*<a\b[^>]*?\bhref=")([^"]+)("[^>]*>)(.*?)(</a>\s*</li>)',
    re.I | re.S,
)


def fix_footer(footer_html: str) -> tuple[str, int]:
    changed = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal changed
        pre, href, mid, text, post = m.group(1, 2, 3, 4, 5)
        key = normalize(text)
        canonical = TEXT_TO_HUB.get(key)
        if canonical and href != canonical:
            changed += 1
            return f"{pre}{canonical}{mid}{text}{post}"
        return m.group(0)

    new = LI_A_RE.sub(repl, footer_html)
    return new, changed


def process_file(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"[skip non-utf8] {path}")
        return 0
    # Apply the <li><a> rewrite sitewide (every link in a list whose visible
    # text matches a canonical service name should point to the hub). This
    # covers footer, header nav, sitemap, and homepage "Core Directions".
    new_text, total = fix_footer(text)
    if total > 0:
        path.write_bytes(new_text.encode("utf-8"))
    return total


SKIP_DIRS = {".git", "node_modules", ".venv", "img", "img-quality", "old-images",
             "css", "js", "fonts"}


def main() -> None:
    files_changed = 0
    total_fixes = 0
    for html in ROOT.rglob("*.html"):
        if any(part in SKIP_DIRS for part in html.parts):
            continue
        n = process_file(html)
        if n:
            files_changed += 1
            total_fixes += n
            print(f"[{n:>2}] {html.relative_to(ROOT)}")
    print(f"\nFiles changed: {files_changed}")
    print(f"Total href fixes: {total_fixes}")


if __name__ == "__main__":
    main()
