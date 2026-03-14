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
        self.nav_links = []       # hrefs inside <nav id="siteNav">
        self.footer_links = []    # hrefs inside <footer class="site-footer">...
        self.has_doctype = False
        self.has_html_tag = False
        self.has_body_close = False
        self.has_site_nav = False
        self.has_site_footer = False
        self._raw = ""
        self._in_site_nav = False
        self._in_site_footer = False

    def feed(self, data):
        self._raw = data
        # Check raw string for certain markers (faster than parse events)
        lower = data.lower()
        self.has_doctype = "<!doctype html" in lower
        self.has_html_tag = "<html" in lower
        self.has_body_close = "</body>" in lower
        # has_site_nav / has_site_footer are detected via parsed tags for precision
        super().feed(data)

    @staticmethod
    def _attrs_dict(attrs):
        return {k: v for k, v in attrs}

    @staticmethod
    def _class_has(class_value: str | None, token: str) -> bool:
        if not class_value:
            return False
        return token in class_value.split()

    def handle_starttag(self, tag, attrs):
        attrs_d = self._attrs_dict(attrs)

        if tag == "nav":
            if (attrs_d.get("id") or "") == "siteNav":
                self._in_site_nav = True
                self.has_site_nav = True

        if tag == "footer":
            if self._class_has(attrs_d.get("class"), "site-footer"):
                self._in_site_footer = True
                self.has_site_footer = True

        if tag == "a":
            val = attrs_d.get("href")
            if val:
                self.links.append(val)
                if self._in_site_nav:
                    self.nav_links.append(val)
                if self._in_site_footer:
                    self.footer_links.append(val)

    def handle_endtag(self, tag):
        if tag == "nav" and self._in_site_nav:
            self._in_site_nav = False
        if tag == "footer" and self._in_site_footer:
            self._in_site_footer = False

# ── helpers ──────────────────────────────────────────────────────────────────

def resolve_paths(href: str) -> list[Path] | None:
    """
    Convert a root-relative href to a filesystem Path.
    Returns None if the path should be skipped (anchor, external, mailto).
    Returns candidate Paths to check (may not exist).
    """
    if not href.startswith("/"):
        return None
    if href.startswith("/#") or href.startswith("//#"):
        return None  # anchor
    if href.startswith("//") or href.startswith("/http"):
        return None  # protocol-relative or weird
    clean = href.split("#")[0].split("?")[0]
    if clean in ("", "/"):
        return [ROOT / "index.html"]

    # ".../" should map to ".../index.html"
    if clean.endswith("/"):
        return [ROOT / clean.lstrip("/") / "index.html"]

    path_part = clean.lstrip("/")
    suffix = Path(path_part).suffix.lower()

    # If the URL already points to a file (e.g. "/foo/bar.html"), check it as-is.
    if suffix:
        return [ROOT / path_part]

    # Otherwise, allow both "dir/index.html" and "file.html" forms.
    return [
        ROOT / path_part / "index.html",
        ROOT / (path_part + ".html"),
    ]

def link_exists(href: str) -> tuple[bool, str]:
    """Return (exists, resolved_path_str)."""
    candidates = resolve_paths(href)
    if candidates is None:
        return (True, "skipped")
    for p in candidates:
        if p.exists():
            return (True, str(p))
    return (False, " OR ".join(str(p) for p in candidates))

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

# ── MAIN AUDIT ────────────────────────────────────────────────────────────────

def audit():
    html_files = collect_html_files()
    total_pages = len(html_files)

    print(f"Found {total_pages} HTML files under {ROOT}\n")

    structural_issues = []          # (path, list_of_issues)
    all_broken_links = defaultdict(list)  # href → [page, page, ...]
    nav_issues = defaultdict(list)  # href → [page, page, ...]
    footer_broken = defaultdict(list)  # href → [page, page, ...]
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
            if nav_href not in parser.nav_links:
                nav_issues[nav_href].append(str(rel))

        # ── Footer link audit (actual footer links used on the page) ─────
        for href in parser.footer_links:
            if not href.startswith("/") or href.startswith("//"):
                continue
            if href.startswith("/#"):
                continue
            exists, _ = link_exists(href)
            if not exists:
                footer_broken[href].append(str(rel))

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
    if footer_broken:
        broken_sorted = sorted(footer_broken.items(), key=lambda x: -len(x[1]))
        for href, pages in broken_sorted:
            print(f"    BROKEN: {href}  (referenced on {len(pages)} page(s))")
            for p in pages[:10]:
                print(f"      {p}")
            if len(pages) > 10:
                print(f"      ... and {len(pages)-10} more")
    else:
        print("    None — all footer link destinations resolve correctly!")

    print("\n" + "=" * 70)
    print("END OF REPORT")
    print("=" * 70)

if __name__ == "__main__":
    audit()
