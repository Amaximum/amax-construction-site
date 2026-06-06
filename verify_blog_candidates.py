"""verify_blog_candidates.py

For every blog candidate produced by restructure_hubs.classify_blog,
open the HTML and decide whether it is REALLY a blog post or a
service/landing-style page disguised as a blog.

Heuristic — a real blog post has at LEAST ONE of:
  - <div class="blog-hero"> or <article ...>
  - <span class="category"> + <span class="date">  (article meta block)
  - "@type": "BlogPosting" or "@type": "Article"
  - og:type article
  - <div class="article-meta"> or class containing 'article-body'

A landing/service page is detected by presence (without the above) of:
  - class="hero"  + service grid (cards) + locations section
  - "@type": "LocalBusiness" + "@type": "Service" without article markers
  - <section ... id="services" or id="service-types">

If neither pure blog nor pure landing → mark unclear.

Usage:
  python verify_blog_candidates.py
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

# Force utf-8 stdout so we can print emoji-bearing titles.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

import restructure_hubs as rh  # noqa: E402

ROOT = rh.ROOT


BLOG_MARKERS = [
    re.compile(r'<div\s+class="blog-hero"', re.I),
    re.compile(r'<article\b', re.I),
    re.compile(r'<div\s+class="article-meta"', re.I),
    re.compile(r'<div\s+class="article-body"', re.I),
    re.compile(r'class="page-blog"', re.I),
    re.compile(r'"@type"\s*:\s*"BlogPosting"', re.I),
    re.compile(r'"@type"\s*:\s*"Article"', re.I),
    re.compile(r'og:type"\s+content="article"', re.I),
    re.compile(r'<span\s+class="category"', re.I),
]

LANDING_MARKERS = [
    re.compile(r'id="service-types"', re.I),
    re.compile(r'id="how-it-works"', re.I),
    re.compile(r'id="locations"', re.I),
    re.compile(r'class="cta-strip"', re.I),
    re.compile(r'"@type"\s*:\s*"Service"', re.I),
]


def classify_content(html: str) -> tuple[str, list[str], list[str]]:
    blog_hits = [m.pattern for m in BLOG_MARKERS if m.search(html)]
    land_hits = [m.pattern for m in LANDING_MARKERS if m.search(html)]
    if blog_hits and not land_hits:
        return ('blog', blog_hits, land_hits)
    if blog_hits and land_hits:
        # Both present — blog post that uses some hub-like sections at the bottom.
        # This is normal for many of these pages (article + cross-link sections).
        # Treat as blog if STRONG blog marker present.
        strong = any(p in blog_hits for p in (
            r'<div\s+class="blog-hero"',
            r'<article\b',
            r'<div\s+class="article-meta"',
            r'<div\s+class="article-body"',
            r'"@type"\s*:\s*"BlogPosting"',
            r'"@type"\s*:\s*"Article"',
            r'og:type"\s+content="article"',
        ))
        return ('blog' if strong else 'mixed', blog_hits, land_hits)
    if land_hits and not blog_hits:
        return ('landing', blog_hits, land_hits)
    return ('unknown', blog_hits, land_hits)


def main() -> int:
    # Run a partial discovery to get candidate list (mirror of restructure_hubs.main).
    locations: dict[str, list] = {s['hub_dir']: [] for s in rh.SERVICES}
    blog_candidates: list[tuple[str, str, str | None]] = []
    duplicate_hubs: list[str] = []

    candidate_dirs: list[Path] = []
    for d in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        name = d.name
        if name.startswith('.') or name in rh.SKIP_DIRS or name == 'blog':
            continue
        if (d / 'index.html').exists():
            candidate_dirs.append(d)

    blog_root = ROOT / 'blog'
    if blog_root.is_dir():
        for d in sorted(p for p in blog_root.iterdir() if p.is_dir()):
            if d.name.startswith('.'):
                continue
            if (d / 'index.html').exists():
                candidate_dirs.append(d)

    for d in candidate_dirs:
        rel = d.relative_to(ROOT).as_posix()
        if '/' in rel:
            html = rh.read_html(d / 'index.html')
            hub, city = rh.classify_blog(rel.replace('/', '-'), html)
            if hub:
                blog_candidates.append((rel, hub, city))
            continue

        if rel in rh.DUPLICATE_HUB_SLUGS:
            duplicate_hubs.append(rel)
            continue

        kind, hub_dir, city = rh.classify_dir(rel)
        if kind == 'hub':
            continue
        if kind == 'location':
            locations[hub_dir].append((f'/{rel}/', city, rh.CITIES[city]))
            continue

        html = rh.read_html(d / 'index.html')
        hub, city = rh.classify_blog(rel, html)
        if hub:
            blog_candidates.append((rel, hub, city))

    # Inspect content for each.
    blog_real: list[tuple[str, str, str | None, str]] = []
    landings: list[tuple[str, str, str | None, str]] = []
    mixed: list[tuple[str, str, str | None, str]] = []
    unknown: list[tuple[str, str, str | None, str]] = []

    for rel, hub, city in blog_candidates:
        html = rh.read_html(ROOT / rel / 'index.html')
        kind, _bh, _lh = classify_content(html)
        title = rh.extract_title(html)
        row = (rel, hub, city, title[:90])
        if kind == 'blog':
            blog_real.append(row)
        elif kind == 'landing':
            landings.append(row)
        elif kind == 'mixed':
            mixed.append(row)
        else:
            unknown.append(row)

    def dump(label: str, rows: list[tuple[str, str, str | None, str]]):
        print(f'\n===== {label} ({len(rows)}) =====')
        for rel, hub, city, title in rows:
            citystr = city or '-'
            print(f'  {rel:<68} hub={hub:<42} city={citystr:<14} | {title}')

    dump('REAL BLOG POSTS  (will be linked from hubs / locations)', blog_real)
    dump('LANDING / SERVICE-LIKE  (should be EXCLUDED from related-articles)', landings)
    dump('MIXED  (article markers + landing markers; treated as BLOG)', mixed)
    dump('UNKNOWN  (no clear markers either way)', unknown)

    print('\n----- summary -----')
    print(f'real blogs: {len(blog_real)}')
    print(f'landings:   {len(landings)}')
    print(f'mixed:      {len(mixed)}')
    print(f'unknown:    {len(unknown)}')
    print(f'duplicate hubs (already excluded): {len(duplicate_hubs)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
