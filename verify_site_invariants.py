#!/usr/bin/env python3
"""Verify invariants for the aMaximum Construction static site.

This script checks published content pages, booking routes, widgets, and heading
structure. Vercel redirect sources and service templates are not published pages.

Exit code:
- 0: all checks pass
- 1: one or more errors
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit


ELFSIGHT_LOADER_SRC = "https://static.elfsight.com/platform/platform.js"
ELFSIGHT_OLD_LOADER_RE = re.compile(r"elfsightcdn\.com/platform\.js", re.I)
ELFSIGHT_ANY_LOADER_RE = re.compile(
    r"<script\b[^>]*\bsrc\s*=\s*[\"'][^\"']*elfsight[^\"']*[\"'][^>]*>\s*</script\s*>",
    re.I,
)
SCRIPT_TAG_RE = re.compile(r"<script\b(?P<attrs>[^>]*)>(?P<body>.*?)</script\s*>", re.I | re.S)
ELFSIGHT_DYNAMIC_CREATE_RE = re.compile(r"document\.createElement\(\s*[\"']script[\"']\s*\)", re.I)
ELFSIGHT_DYNAMIC_SRC_RE = re.compile(
    rf"\.src\s*=\s*[\"']{re.escape(ELFSIGHT_LOADER_SRC)}[\"']",
    re.I,
)
ELFSIGHT_DYNAMIC_DEFER_RE = re.compile(r"\.\s*defer\s*=\s*true\b", re.I)

RATING_APP_CLASS = "elfsight-app-3935cedc-67a1-44d8-b85e-f841374ae875"
REVIEWS_APP_CLASS = "elfsight-app-b029cad3-6f49-425c-9793-f556870797bb"

BOOKING_FORM_FILES = {
    "/book-now/": "book-now/index.html",
    "/book-basement.html": "book-basement.html",
    "/book-bathroom.html": "book-bathroom.html",
    "/book-canopy.html": "book-canopy.html",
    "/book-carpentry.html": "book-carpentry.html",
    "/book-christmas.html": "book-christmas.html",
    "/book-contractor.html": "book-contractor.html",
    "/book-deck.html": "book-deck.html",
    "/book-demolition.html": "book-demolition.html",
    "/book-electrical.html": "book-electrical.html",
    "/book-excavation.html": "book-excavation.html",
    "/book-fence.html": "book-fence.html",
    "/book-handy.html": "book-handy.html",
    "/book-interlock.html": "book-interlock.html",
    "/book-landscaping.html": "book-landscaping.html",
    "/book-painting.html": "book-painting.html",
    "/book-plumbing.html": "book-plumbing.html",
    "/book-railing.html": "book-railing.html",
    "/book-renovation.html": "book-renovation.html",
}
BOOKING_PAGE_FILES = {path.lower() for path in BOOKING_FORM_FILES.values()}
SITE_HOSTS = {"amaximumconstruction.com", "www.amaximumconstruction.com"}
FORM_TAG_RE = re.compile(r"<form\b", re.I)

SITE_JS_RE = re.compile(r"<script[^>]+src=[\"']/js/site\.js(?:\?[^\"']*)?[\"'][^>]*>\s*</script>", re.I)

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


class HeadingParser(HTMLParser):
    """Collect headings in document order with their text content."""

    def __init__(self) -> None:
        super().__init__()
        self._level: int | None = None
        self._text_parts: list[str] = []
        self.headings: list[tuple[int, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        tag = tag.lower()
        if len(tag) == 2 and tag.startswith("h") and tag[1].isdigit():
            level = int(tag[1])
            if 1 <= level <= 6:
                self._level = level
                self._text_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._level is None:
            return
        if tag == f"h{self._level}":
            text = " ".join("".join(self._text_parts).split())
            self.headings.append((self._level, text))
            self._level = None
            self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._level is not None and data:
            self._text_parts.append(data)


@dataclass(frozen=True)
class Finding:
    path: str
    message: str


def iter_html_files(root: Path) -> Iterable[Path]:
    """Yield HTML files that represent published pages.

    Hidden build output, service templates, SEO working files, and Vercel redirect
    sources are not independent published pages.
    """

    skip_name_re = re.compile(r"^(service-template\.html|index-seo-.*\.html)$", re.I)
    redirect_sources = load_redirect_sources(root)
    for p in sorted(root.rglob("*.html")):
        relative = p.relative_to(root)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if skip_name_re.match(p.name):
            continue
        route = html_file_route(relative.as_posix())
        if any(is_redirect_source(route, source) for source in redirect_sources):
            continue
        yield p


def load_redirect_sources(root: Path) -> tuple[str, ...]:
    """Load Vercel redirect sources so aliases are not checked as content pages."""

    config_path = root / "vercel.json"
    if not config_path.exists():
        return ()

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read Vercel redirect configuration: {error}") from error

    redirects = config.get("redirects", []) if isinstance(config, dict) else None
    if not isinstance(redirects, list):
        raise ValueError("Vercel configuration must contain a redirects list")

    sources: list[str] = []
    for index, redirect in enumerate(redirects):
        if not isinstance(redirect, dict) or not isinstance(redirect.get("source"), str):
            raise ValueError(f"Vercel redirect at index {index} has no string source")
        source = redirect["source"]
        if (":" in source or "*" in source) and not source.endswith("/:path*"):
            raise ValueError(f"Unsupported Vercel redirect pattern: {source}")
        sources.append(source)

    return tuple(sources)


def html_file_route(relative_path: str) -> str:
    """Convert an HTML file path to its root-relative public route."""

    if relative_path.lower() == "index.html":
        return "/"
    if relative_path.lower().endswith("/index.html"):
        return "/" + relative_path[: -len("/index.html")]
    return "/" + relative_path


def normalize_route(route: str) -> str:
    return route.rstrip("/") or "/"


def is_redirect_source(route: str, source: str) -> bool:
    """Return whether a public route is covered by an exact or :path* redirect."""

    route = normalize_route(route)
    source = normalize_route(source)
    wildcard = "/:path*"
    if source.endswith(wildcard):
        prefix = normalize_route(source[: -len(wildcard)])
        return prefix == "/" or route == prefix or route.startswith(prefix + "/")
    return route == source


def rel_posix(root: Path, file_path: Path) -> str:
    return file_path.relative_to(root).as_posix()


def dynamic_elfsight_loaders(html: str) -> list[str]:
    """Find inline scripts that create and configure the Elfsight platform loader."""

    loaders: list[str] = []
    for match in SCRIPT_TAG_RE.finditer(html):
        if re.search(r"\bsrc\s*=", match.group("attrs"), re.I):
            continue
        body = match.group("body")
        if ELFSIGHT_DYNAMIC_CREATE_RE.search(body) and ELFSIGHT_DYNAMIC_SRC_RE.search(body):
            loaders.append(body)
    return loaders


def has_elfsight_loader_ok(html: str) -> tuple[bool, str]:
    if ELFSIGHT_OLD_LOADER_RE.search(html):
        return (False, "Old Elfsight loader (elfsightcdn.com) present")

    static_loaders = ELFSIGHT_ANY_LOADER_RE.findall(html)
    dynamic_loaders = dynamic_elfsight_loaders(html)
    loader_count = len(static_loaders) + len(dynamic_loaders)
    if loader_count == 0:
        return (False, "Missing Elfsight loader script or recognized dynamic loader")
    if loader_count != 1:
        return (False, f"Expected exactly 1 Elfsight loader, found {loader_count}")

    if static_loaders:
        tag = static_loaders[0]
        if not re.search(
            rf"\bsrc\s*=\s*[\"']{re.escape(ELFSIGHT_LOADER_SRC)}[\"']",
            tag,
            re.I,
        ):
            return (False, "Unexpected Elfsight loader URL")
        if not re.search(r"\bdefer(?:\s|=|/|>)", tag, re.I):
            return (False, "Elfsight loader must use defer")
    elif not ELFSIGHT_DYNAMIC_DEFER_RE.search(dynamic_loaders[0]):
        return (False, "Dynamic Elfsight loader must set defer")

    return (True, "")


def count_elfsight_loader_tags(html: str) -> int:
    return len(ELFSIGHT_ANY_LOADER_RE.findall(html)) + len(dynamic_elfsight_loaders(html))


def booking_route_for_href(href: str) -> str | None:
    """Return an allowed booking route for a local or same-site href."""

    try:
        parsed = urlsplit(href.strip())
    except ValueError:
        return None

    if parsed.scheme or parsed.netloc:
        if parsed.scheme.lower() not in {"http", "https"} or parsed.hostname not in SITE_HOSTS:
            return None
        route = parsed.path
    else:
        route = parsed.path
        if not route.startswith("/"):
            return None

    return route if route in BOOKING_FORM_FILES else None


def verify_booking_forms(root: Path) -> tuple[set[str], list[Finding]]:
    """Verify every allowed booking route resolves to an HTML form."""

    valid_routes: set[str] = set()
    errors: list[Finding] = []
    for route, relative_path in BOOKING_FORM_FILES.items():
        form_path = root / relative_path
        if not form_path.is_file():
            errors.append(Finding(relative_path, f"Allowed booking route {route} has no target file"))
            continue
        try:
            form_html = form_path.read_text(encoding="utf-8", errors="replace")
        except OSError as error:
            errors.append(Finding(relative_path, f"Could not read booking form: {error}"))
            continue
        if not FORM_TAG_RE.search(form_html):
            errors.append(Finding(relative_path, f"Allowed booking route {route} does not contain a form"))
            continue
        valid_routes.add(route)
    return valid_routes, errors


def has_html_id(html: str, element_id: str) -> bool:
    return bool(re.search(rf"\bid\s*=\s*([\"']){re.escape(element_id)}\1", html, re.I))


def verify_page(
    root: Path,
    file_path: Path,
    html: str,
    valid_booking_routes: set[str],
) -> tuple[list[Finding], list[Finding]]:
    """Return (errors, warnings)."""

    rel = rel_posix(root, file_path)
    errors: list[Finding] = []
    warnings: list[Finding] = []

    is_booking = rel.lower() in BOOKING_PAGE_FILES

    if not SITE_JS_RE.search(html):
        errors.append(Finding(rel, "Missing global /js/site.js include (mobile menu may not work)"))

    if not is_booking:
        ok, reason = has_elfsight_loader_ok(html)
        if not ok:
            errors.append(Finding(rel, reason))

        if "data-elfsight-app-lazy" in html.lower():
            errors.append(Finding(rel, "Found data-elfsight-app-lazy (should be removed)"))

        if not has_html_id(html, "rating-widget"):
            errors.append(Finding(rel, "Missing #rating-widget wrapper"))
        if RATING_APP_CLASS not in html:
            errors.append(Finding(rel, f"Missing rating app class {RATING_APP_CLASS}"))
        if not has_html_id(html, "reviews-embed"):
            errors.append(Finding(rel, "Missing #reviews-embed wrapper"))
        if REVIEWS_APP_CLASS not in html:
            errors.append(Finding(rel, f"Missing reviews app class {REVIEWS_APP_CLASS}"))

    # BOOK NOW CTAs
    parser = AnchorTextParser()
    try:
        parser.feed(html)
    except Exception:
        warnings.append(Finding(rel, "HTML parse warning while scanning anchors"))

    book_now_anchors = [(href, text) for (href, text) in parser.anchors if text.strip().upper() == "BOOK NOW"]
    if not is_booking and not book_now_anchors:
        # Some pages might not have a BOOK NOW CTA (rare), so warning only
        warnings.append(Finding(rel, "No BOOK NOW anchor found"))
    for href, _ in book_now_anchors:
        route = booking_route_for_href(href)
        if route is None:
            errors.append(Finding(rel, f"BOOK NOW anchor must use an allowed booking route (found {href!r})"))
        elif route not in valid_booking_routes:
            errors.append(Finding(rel, f"BOOK NOW anchor targets a missing or invalid form route (found {href!r})"))

    heading_parser = HeadingParser()
    try:
        heading_parser.feed(html)
    except Exception:
        warnings.append(Finding(rel, "HTML parse warning while scanning headings"))
    else:
        headings = heading_parser.headings
        if not headings:
            errors.append(Finding(rel, "Missing page heading structure (no H1-H6 tags found)"))
        else:
            h1_count = sum(1 for level, _ in headings if level == 1)
            if h1_count != 1:
                errors.append(Finding(rel, f"Expected exactly 1 H1 heading, found {h1_count}"))

            first_level, first_text = headings[0]
            if first_level != 1:
                label = first_text or "(empty heading)"
                errors.append(Finding(rel, f"First heading must be H1 (found H{first_level}: {label!r})"))

            previous_level = first_level
            for level, text in headings[1:]:
                if level > previous_level + 1:
                    label = text or "(empty heading)"
                    errors.append(
                        Finding(rel, f"Heading hierarchy skips from H{previous_level} to H{level} at {label!r}")
                    )
                previous_level = level

    # Google Places Autocomplete should only be on booking forms.
    has_places = bool(GOOGLE_PLACES_RE.search(html) or GOOGLE_PLACES_CB_RE.search(html))
    if is_booking and not has_places:
        errors.append(Finding(rel, "Booking page missing Google Places loader/callback markers"))
    if (not is_booking) and has_places:
        errors.append(Finding(rel, "Non-booking page must not include Google Places loader"))

    # Optional: detect unexpected forms
    if (not is_booking) and FORM_TAG_RE.search(html):
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

    try:
        html_files = list(iter_html_files(root))
    except (OSError, ValueError) as error:
        print(f"Could not determine published HTML inventory: {error}", file=sys.stderr)
        return 1
    if not html_files:
        print(f"No HTML files found under: {root}", file=sys.stderr)
        return 1

    all_errors: list[Finding] = []
    all_warnings: list[Finding] = []
    valid_booking_routes, booking_form_errors = verify_booking_forms(root)
    all_errors.extend(booking_form_errors)

    for file_path in html_files:
        try:
            html = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            all_errors.append(Finding(rel_posix(root, file_path), f"Read error: {e}"))
            continue

        errors, warnings = verify_page(root, file_path, html, valid_booking_routes)
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
