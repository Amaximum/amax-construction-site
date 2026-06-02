#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent


def find_first(pattern: str, text: str, flags: int = 0) -> str | None:
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None


def count_matches(pattern: str, text: str, flags: int = 0) -> int:
    return len(re.findall(pattern, text, flags))


def check_heading_hierarchy(html: str) -> tuple[bool, str]:
    heads = re.findall(r"<h([1-6])[^>]*>", html, flags=re.IGNORECASE)
    if not heads:
        return False, "No headings found"
    levels = [int(h) for h in heads]
    prev = levels[0]
    for lvl in levels[1:]:
        if lvl - prev > 1:
            return False, f"Heading jump from h{prev} to h{lvl}"
        prev = lvl
    return True, f"{len(levels)} headings with proper hierarchy"


def extract_schema_types(html: str) -> set[str]:
    types: set[str] = set()
    blocks = re.findall(
        r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    for block in blocks:
        raw = block.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
            stack = [obj]
            while stack:
                cur = stack.pop()
                if isinstance(cur, dict):
                    t = cur.get("@type")
                    if isinstance(t, str):
                        types.add(t)
                    elif isinstance(t, list):
                        for item in t:
                            if isinstance(item, str):
                                types.add(item)
                    for v in cur.values():
                        stack.append(v)
                elif isinstance(cur, list):
                    stack.extend(cur)
        except Exception:
            for t in re.findall(r'"@type"\s*:\s*"([^"]+)"', raw):
                types.add(t)
    return types


def yes(condition: bool) -> str:
    return "PASS" if condition else "FAIL"


def audit_page(page_path: Path) -> list[tuple[str, bool, str]]:
    html = page_path.read_text(encoding="utf-8")
    results: list[tuple[str, bool, str]] = []

    title = find_first(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    title_len_ok = bool(title and 35 <= len(re.sub(r"\s+", " ", title)) <= 70)
    results.append(("Page Title", title_len_ok, f"Title is {len(title or '')} chars: \"{title or ''}\""))

    meta_desc = find_first(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    desc_len_ok = bool(meta_desc and 110 <= len(meta_desc) <= 170)
    results.append(("Meta Description", desc_len_ok, f"Meta description is {len(meta_desc or '')} chars."))

    canonical = find_first(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    canonical_ok = bool(canonical and canonical.startswith("https://"))
    results.append(("Canonical Tag", canonical_ok, f"Canonical tag found: {canonical or 'missing'}"))

    h1_count = count_matches(r"<h1[^>]*>.*?</h1>", html, re.IGNORECASE | re.DOTALL)
    h1 = find_first(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    results.append(("H1 Heading", h1_count == 1, f"{h1_count} H1 found: \"{re.sub(r'<[^>]+>', '', h1 or '').strip()}\""))

    hh_ok, hh_msg = check_heading_hierarchy(html)
    results.append(("Heading Hierarchy", hh_ok, hh_msg))

    imgs = re.findall(r"<img\b[^>]*>", html, re.IGNORECASE)
    missing_alt = [tag for tag in imgs if not re.search(r'alt=["\'][^"\']*["\']', tag, flags=re.IGNORECASE)]
    results.append(("Image Alt Text", len(missing_alt) == 0, f"All {len(imgs)} images have alt text." if not missing_alt else f"{len(missing_alt)} images missing alt."))

    og_required = ["og:type", "og:title", "og:description", "og:url", "og:image"]
    og_ok = all(re.search(rf'<meta\s+property=["\']{re.escape(k)}["\']', html, flags=re.IGNORECASE) for k in og_required)
    results.append(("Open Graph Tags", og_ok, "All core Open Graph tags present." if og_ok else "Missing one or more OG tags."))

    tw = find_first(r'<meta\s+name=["\']twitter:card["\']\s+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    results.append(("Twitter Card", bool(tw), f"Twitter card type: {tw or 'missing'}"))

    schema_types = extract_schema_types(html)
    results.append(("Schema Markup", len(schema_types) > 0, f"Found structured data types: {', '.join(sorted(schema_types)) if schema_types else 'none'}"))
    results.append(("FAQ Schema", "FAQPage" in schema_types, "FAQPage schema found." if "FAQPage" in schema_types else "FAQPage schema missing."))
    results.append(("Breadcrumb Schema", "BreadcrumbList" in schema_types, "BreadcrumbList schema found." if "BreadcrumbList" in schema_types else "BreadcrumbList schema missing."))

    robots = ROOT / "robots.txt"
    robots_ok = robots.exists() and "sitemap:" in robots.read_text(encoding="utf-8", errors="ignore").lower()
    results.append(("robots.txt", robots_ok, "robots.txt exists and contains a Sitemap directive." if robots_ok else "robots.txt missing or no Sitemap directive."))

    sitemap = ROOT / "sitemap.xml"
    sitemap_ok = sitemap.exists()
    results.append(("XML Sitemap", sitemap_ok, "sitemap.xml found." if sitemap_ok else "sitemap.xml missing."))

    robots_meta = find_first(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    robots_meta_ok = bool(robots_meta and "index" in robots_meta.lower() and "follow" in robots_meta.lower())
    results.append(("Robots Meta Tag", robots_meta_ok, f"Robots meta: \"{robots_meta or 'missing'}\""))

    llms_file = ROOT / "llms.txt"
    results.append(("llms.txt", llms_file.exists(), "llms.txt found." if llms_file.exists() else "llms.txt missing."))

    llms_link = re.search(r'<link\s+[^>]*href=["\']https://www\.amaximumconstruction\.com/llms\.txt["\']', html, re.IGNORECASE)
    results.append(("llms.txt Discovery Link", bool(llms_link), "HTML head links to llms.txt." if llms_link else "llms.txt head link missing."))

    viewport = find_first(r'<meta\s+name=["\']viewport["\']\s+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    results.append(("Viewport Meta", bool(viewport), f"Viewport tag found: {viewport or 'missing'}"))

    lang = find_first(r"<html[^>]*\slang=[\"']([^\"']+)[\"']", html, re.IGNORECASE)
    results.append(("HTML Lang Attribute", bool(lang), f"Language set: {lang or 'missing'}"))

    https_ok = bool(canonical and canonical.startswith("https://"))
    results.append(("HTTPS", https_ok, "Canonical uses HTTPS." if https_ok else "Canonical is not HTTPS."))

    hreflang_count = count_matches(r'<link\s+rel=["\']alternate["\'][^>]*hreflang=', html, re.IGNORECASE)
    results.append(("Hreflang Tags", True, "Single-language site (lang=\"en\") — hreflang optional." if hreflang_count == 0 else f"Found {hreflang_count} hreflang tag(s)."))

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate location page against QA SEO checklist.")
    parser.add_argument("page", help="Relative path to page HTML file, e.g. deck-contractor-in-thornhill/index.html")
    args = parser.parse_args()

    page_path = ROOT / args.page
    if not page_path.exists():
        raise SystemExit(f"Page not found: {args.page}")

    rows = audit_page(page_path)
    all_ok = True
    for name, ok, msg in rows:
        all_ok = all_ok and ok
        print(f"{'PASS' if ok else 'FAIL'} | {name} | {msg}")

    print("\nSUMMARY:", "PASS" if all_ok else "FAIL")


if __name__ == "__main__":
    main()
