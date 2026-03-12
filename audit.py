#!/usr/bin/env python3
"""
Comprehensive audit script for aMaximum Construction static site.
"""

import os
import sys
from html.parser import HTMLParser
from collections import defaultdict
from pathlib import Path

ROOT = Path("c:/Users/maxim/Desktop/amax-Construction-site")

# ── HTML parser ─────────────────────────────────────────────────────────────

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []           # all href values
        self.has_doctype = False
        self.has_html_tag = False
        self.has_body_close = False
        self.has_site_nav = False
        self.has_site_footer = False
        self._raw = ""

    def feed(self, data):
        self._raw = data
        # Check raw string for certain markers (faster than parse events)
        lower = data.lower()
        self.has_doctype = "<!doctype html" in lower
        self.has_html_tag = "<html" in lower
        self.has_body_close = "</body>" in lower
        self.has_site_nav = 'id="sitenav"' in lower or "id='sitenav'" in lower
        self.has_site_footer = 'class="site-footer"' in lower or "site-footer" in data
        super().feed(data)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, val in attrs:
                if name == "href" and val:
                    self.links.append(val)

# ── helpers ──────────────────────────────────────────────────────────────────

def resolve_path(href: str) -> Path | None:
    """
    Convert a root-relative href to a filesystem Path.
    Returns None if the path should be skipped (anchor, external, mailto).
    Returns Path to check (may not exist).
    """
    if not href.startswith("/"):
        return None
    if href.startswith("/#") or href.startswith("//#"):
        return None  # anchor
    if href.startswith("//") or href.startswith("/http"):
        return None  # protocol-relative or weird
    # Strip anchor fragment
    clean = href.split("#")[0].rstrip("/")
    if not clean or clean == "":
        # bare "/" → index.html
        return ROOT / "index.html"
    # Try as-is + index.html, then as .html
    candidate_dir = ROOT / clean.lstrip("/") / "index.html"
    candidate_file = ROOT / (clean.lstrip("/") + ".html")
    # We return both options; caller checks existence
    return (candidate_dir, candidate_file)

def link_exists(href: str) -> tuple[bool, str]:
    """Return (exists, resolved_path_str)."""
    result = resolve_path(href)
    if result is None:
        return (True, "skipped")
    if isinstance(result, Path):
        # bare "/"
        return (result.exists(), str(result))
    dir_path, file_path = result
    if dir_path.exists():
        return (True, str(dir_path))
    if file_path.exists():
        return (True, str(file_path))
    return (False, f"{dir_path} OR {file_path}")

def collect_html_files():
    return sorted(ROOT.rglob("*.html"))

# ── NAV expected links ────────────────────────────────────────────────────────

NAV_LINKS = [
    "/",
    "/#services",   # skip
    "/locations/",
    "/blog/",
    "/portfolio/",
    "/#contact",    # skip
]

# ── FOOTER expected links ─────────────────────────────────────────────────────

FOOTER_SERVICE_LINKS = [
    "/deck-builder-toronto/",
    "/deck-builder-markham/",
    "/deck-builder-richmond-hill/",
    "/deck-builder-vaughan/",
    "/deck-builder-mississauga/",
    "/services/handyman-plumbing.html",
]

FOOTER_AREA_LINKS = [
    "/locations/",
    "/locations/markham/",
    "/locations/richmond-hill/",
    "/locations/vaughan/",
    "/locations/mississauga/",
]

# ── MAIN AUDIT ────────────────────────────────────────────────────────────────

def audit():
    html_files = collect_html_files()
    total_pages = len(html_files)

    print(f"Found {total_pages} HTML files under {ROOT}\n")

    structural_issues = []          # (path, list_of_issues)
    all_broken_links = defaultdict(list)  # href → [page, page, ...]
    nav_issues = defaultdict(list)  # href → [page, page, ...]
    footer_issues = defaultdict(list)
    homepage_broken = []
    total_internal_links = 0

    for html_file in html_files:
        rel = html_file.relative_to(ROOT)
        try:
            content = html_file.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            structural_issues.append((str(rel), [f"Read error: {e}"]))
            continue

        # ── Structural checks ────────────────────────────────────────────
        issues = []
        if html_file.stat().st_size == 0:
            issues.append("Empty file")
        parser = LinkParser()
        parser.feed(content)

        if not parser.has_doctype:
            issues.append("Missing <!DOCTYPE html>")
        if not parser.has_html_tag:
            issues.append("Missing <html>")
        if not parser.has_body_close:
            issues.append("Missing </body>")
        if not parser.has_site_nav:
            issues.append("Missing nav id='siteNav'")
        if not parser.has_site_footer:
            issues.append("Missing .site-footer")

        if issues:
            structural_issues.append((str(rel), issues))

        # ── Internal link audit ──────────────────────────────────────────
        internal_hrefs = [h for h in parser.links if h.startswith("/") and not h.startswith("//")]
        total_internal_links += len(internal_hrefs)

        for href in internal_hrefs:
            if href.startswith("/#"):
                continue  # anchor skip
            exists, resolved = link_exists(href)
            if not exists:
                all_broken_links[href].append(str(rel))
                if str(rel) == "index.html":
                    homepage_broken.append(href)

        # ── Nav link audit ───────────────────────────────────────────────
        for nav_href in NAV_LINKS:
            if nav_href.startswith("/#"):
                continue
            if nav_href not in parser.links:
                nav_issues[nav_href].append(str(rel))

        # ── Footer link audit ─────────────────────────────────────────────
        for fl in FOOTER_SERVICE_LINKS + FOOTER_AREA_LINKS:
            exists, _ = link_exists(fl)
            if not exists:
                footer_issues[fl].append("DESTINATION_MISSING")

    # ── Check footer link destinations once ──────────────────────────────
    footer_dest_broken = []
    for fl in FOOTER_SERVICE_LINKS + FOOTER_AREA_LINKS:
        exists, _ = link_exists(fl)
        if not exists:
            footer_dest_broken.append(fl)

    # ── Homepage specific ─────────────────────────────────────────────────
    homepage = ROOT / "index.html"
    homepage_all_broken = []
    if homepage.exists():
        content = homepage.read_text(encoding="utf-8", errors="replace")
        parser = LinkParser()
        parser.feed(content)
        for href in parser.links:
            if href.startswith("/") and not href.startswith("//") and not href.startswith("/#"):
                exists, _ = link_exists(href)
                if not exists:
                    homepage_all_broken.append(href)

    # ── REPORT ────────────────────────────────────────────────────────────
    print("=" * 70)
    print("AUDIT REPORT — aMaximum Construction Site")
    print("=" * 70)

    print(f"\n[1] TOTAL PAGES CHECKED: {total_pages}")

    print(f"\n[2] STRUCTURAL ISSUES ({len(structural_issues)} pages affected):")
    if structural_issues:
        for path, issues in structural_issues:
            print(f"    {path}")
            for iss in issues:
                print(f"      - {iss}")
    else:
        print("    None")

    print(f"\n[3] TOTAL INTERNAL LINKS FOUND: {total_internal_links}")

    broken_sorted = sorted(all_broken_links.items(), key=lambda x: -len(x[1]))
    print(f"\n[4] BROKEN INTERNAL LINK DESTINATIONS ({len(broken_sorted)} unique broken hrefs):")
    if broken_sorted:
        for href, pages in broken_sorted:
            print(f"    {href}  (broken on {len(pages)} page(s))")
            for p in pages[:5]:  # show up to 5 pages
                print(f"      referenced from: {p}")
            if len(pages) > 5:
                print(f"      ... and {len(pages)-5} more")
    else:
        print("    None — all internal links resolve correctly!")

    print(f"\n[5] NAV LINK STATUS:")
    nav_ok = True
    for nav_href in NAV_LINKS:
        if nav_href.startswith("/#"):
            print(f"    {nav_href:40s}  SKIP (anchor)")
            continue
        exists, _ = link_exists(nav_href)
        dest_ok = "OK" if exists else "DESTINATION MISSING"
        pages_missing = nav_issues.get(nav_href, [])
        if pages_missing or not exists:
            nav_ok = False
            print(f"    {nav_href:40s}  {dest_ok}  | Missing from {len(pages_missing)} page(s)")
            for p in pages_missing[:10]:
                print(f"      {p}")
            if len(pages_missing) > 10:
                print(f"      ... and {len(pages_missing)-10} more")
        else:
            print(f"    {nav_href:40s}  {dest_ok}  | Present on all pages")

    print(f"\n[6] HOMEPAGE (index.html) BROKEN LINKS:")
    if homepage_all_broken:
        for href in sorted(set(homepage_all_broken)):
            print(f"    {href}")
    else:
        print("    None — all homepage links resolve correctly!")

    print(f"\n[7] FOOTER LINK DESTINATIONS:")
    if footer_dest_broken:
        for fl in footer_dest_broken:
            print(f"    BROKEN: {fl}")
    else:
        print("    All footer link destinations exist!")

    print("\n" + "=" * 70)
    print("END OF REPORT")
    print("=" * 70)

if __name__ == "__main__":
    audit()
