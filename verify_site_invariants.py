#!/usr/bin/env python3
"""Verify invariants for the aMaximum Construction static site.

This script is meant to "lock in" the expected global behaviors:
- Elfsight loader uses static.elfsight.com and is deferred.
- Rating badge widget exists on every page (fixed bottom-right wrapper).
- Reviews list embed exists on every page except the booking page, and is placed before FAQ.
- BOOK NOW CTAs link to /book-now/.
- Google Places Autocomplete is loaded only on /book-now/.

Exit code:
- 0: all checks pass
- 1: one or more errors
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


ELFSIGHT_LOADER_SRC = "https://static.elfsight.com/platform/platform.js"
ELFSIGHT_OLD_LOADER_RE = re.compile(r"elfsightcdn\.com/platform\.js", re.I)
ELFSIGHT_ANY_LOADER_RE = re.compile(r"<script[^>]+src=[\"'][^\"']*elfsight[^\"']*[\"'][^>]*></script>", re.I)

RATING_APP_CLASS = "elfsight-app-3935cedc-67a1-44d8-b85e-f841374ae875"
REVIEWS_APP_CLASS = "elfsight-app-b029cad3-6f49-425c-9793-f556870797bb"

BOOKING_DIR = "book-now"
BOOKING_PAGE = f"{BOOKING_DIR}/index.html"

SITE_JS_RE = re.compile(r"<script[^>]+src=[\"']/js/site\.js[\"'][^>]*>\s*</script>", re.I)

GOOGLE_PLACES_RE = re.compile(r"maps\.googleapis\.com/maps/api/js\?[^\"']*libraries=places", re.I)
GOOGLE_PLACES_CB_RE = re.compile(r"callback=initAddressAutocomplete", re.I)


class AnchorTextParser(HTMLParser):
    """Collect anchors and their text content (roughly)."""

    def __init__(self) -> None:
        super().__init__()
        self._in_a = False
        self._a_href: str | None = None
        self._a_text_parts: list[str] = []
        self.anchors: list[tuple[str, str]] = []  # (href, text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        self._in_a = True
        self._a_text_parts = []
        self._a_href = None
        for name, val in attrs:
            if name.lower() == "href" and val:
                self._a_href = val

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a":
            return
        if self._in_a:
            href = self._a_href or ""
            text = " ".join("".join(self._a_text_parts).split())
            self.anchors.append((href, text))
        self._in_a = False
        self._a_href = None
        self._a_text_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_a and data:
            self._a_text_parts.append(data)


@dataclass(frozen=True)
class Finding:
    path: str
    message: str


def iter_html_files(root: Path) -> Iterable[Path]:
    """Yield HTML files that represent published pages.

    The repo may contain helper/template HTML files that are not meant to be served
    (e.g., generator templates, SEO working files). We exclude known patterns to
    keep this check focused on the live site.
    """

    skip_name_re = re.compile(r"^(service-template\.html|index-seo-.*\.html)$", re.I)
    for p in sorted(root.rglob("*.html")):
        if any(part.startswith(".") for part in p.parts):
            continue
        if skip_name_re.match(p.name):
            continue
        yield p


def rel_posix(root: Path, file_path: Path) -> str:
    return file_path.relative_to(root).as_posix()


def has_elfsight_loader_ok(html: str) -> tuple[bool, str]:
    # Must include the expected loader with defer
    expected = re.compile(
        rf"<script[^>]+src=[\"']{re.escape(ELFSIGHT_LOADER_SRC)}[\"'][^>]*>",
        re.I,
    )
    m = expected.search(html)
    if not m:
        return (False, "Missing Elfsight loader script")

    tag = m.group(0)
    if "defer" not in tag.lower():
        return (False, "Elfsight loader must use defer")

    if ELFSIGHT_OLD_LOADER_RE.search(html):
        return (False, "Old Elfsight loader (elfsightcdn.com) present")

    return (True, "")


def count_elfsight_loader_tags(html: str) -> int:
    return len(ELFSIGHT_ANY_LOADER_RE.findall(html))


def verify_page(root: Path, file_path: Path, html: str) -> tuple[list[Finding], list[Finding]]:
    """Return (errors, warnings)."""

    rel = rel_posix(root, file_path)
    errors: list[Finding] = []
    warnings: list[Finding] = []

    is_booking = rel.lower() == BOOKING_PAGE

    if not SITE_JS_RE.search(html):
        errors.append(Finding(rel, "Missing global /js/site.js include (mobile menu may not work)"))

    ok, reason = has_elfsight_loader_ok(html)
    if not ok:
        errors.append(Finding(rel, reason))

    loader_count = count_elfsight_loader_tags(html)
    if loader_count != 1:
        errors.append(Finding(rel, f"Expected exactly 1 Elfsight loader script tag, found {loader_count}"))

    if "data-elfsight-app-lazy" in html.lower():
        errors.append(Finding(rel, "Found data-elfsight-app-lazy (should be removed)"))

    # Rating widget must exist everywhere
    if "id=\"rating-widget\"" not in html and "id='rating-widget'" not in html:
        errors.append(Finding(rel, "Missing #rating-widget wrapper"))
    if RATING_APP_CLASS not in html:
        errors.append(Finding(rel, f"Missing rating app class {RATING_APP_CLASS}"))

    # Reviews embed rules
    has_reviews = ("id=\"reviews-embed\"" in html) or ("id='reviews-embed'" in html) or (REVIEWS_APP_CLASS in html)
    if is_booking:
        if has_reviews:
            errors.append(Finding(rel, "Booking page must not include reviews embed"))
    else:
        if not has_reviews:
            errors.append(Finding(rel, "Non-booking page missing reviews embed"))
        else:
            faq_index = html.find('id="faq"')
            if faq_index == -1:
                faq_index = html.find("id='faq'")
            reviews_index = html.find('id="reviews-embed"')
            if reviews_index == -1:
                reviews_index = html.find("id='reviews-embed'")
            if faq_index != -1 and reviews_index != -1 and reviews_index > faq_index:
                errors.append(Finding(rel, "reviews-embed must appear before #faq"))

    # BOOK NOW CTAs
    parser = AnchorTextParser()
    try:
        parser.feed(html)
    except Exception:
        warnings.append(Finding(rel, "HTML parse warning while scanning anchors"))

    book_now_anchors = [(href, text) for (href, text) in parser.anchors if text.strip().upper() == "BOOK NOW"]
    if not book_now_anchors:
        # Some pages might not have a BOOK NOW CTA (rare), so warning only
        warnings.append(Finding(rel, "No BOOK NOW anchor found"))
    for href, _ in book_now_anchors:
        if href != "/book-now/":
            errors.append(Finding(rel, f"BOOK NOW anchor href must be /book-now/ (found {href!r})"))

    # Google Places Autocomplete should only be on booking page
    has_places = bool(GOOGLE_PLACES_RE.search(html) or GOOGLE_PLACES_CB_RE.search(html))
    if is_booking and not has_places:
        errors.append(Finding(rel, "Booking page missing Google Places loader/callback markers"))
    if (not is_booking) and has_places:
        errors.append(Finding(rel, "Non-booking page must not include Google Places loader"))

    # Optional: detect unexpected forms
    if (not is_booking) and ("<form" in html.lower()):
        warnings.append(Finding(rel, "Found <form> on non-booking page (check widget exclusion rules)"))

    return errors, warnings


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parent),
        help="Site root directory (default: script directory)",
    )
    ap.add_argument(
        "--max",
        type=int,
        default=40,
        help="Max findings to print per category (default: 40)",
    )
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Root does not exist: {root}", file=sys.stderr)
        return 1

    html_files = list(iter_html_files(root))
    if not html_files:
        print(f"No HTML files found under: {root}", file=sys.stderr)
        return 1

    all_errors: list[Finding] = []
    all_warnings: list[Finding] = []

    for file_path in html_files:
        try:
            html = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            all_errors.append(Finding(rel_posix(root, file_path), f"Read error: {e}"))
            continue

        errors, warnings = verify_page(root, file_path, html)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    def print_findings(title: str, findings: list[Finding], max_items: int) -> None:
        print("\n" + title)
        print("-" * len(title))
        if not findings:
            print("(none)")
            return
        for f in findings[:max_items]:
            print(f"{f.path}: {f.message}")
        if len(findings) > max_items:
            print(f"... and {len(findings) - max_items} more")

    print(f"Checked {len(html_files)} HTML files under {root}")
    print_findings("ERRORS", all_errors, args.max)
    print_findings("WARNINGS", all_warnings, args.max)

    if all_errors:
        print(f"\nFAILED: {len(all_errors)} error(s), {len(all_warnings)} warning(s)")
        return 1

    print(f"\nOK: 0 errors, {len(all_warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
