"""refresh_sitemap.py

Rebuild sitemap.xml so that:
  - Every indexable page on disk is listed (currently 25 location pages are missing).
  - <lastmod> is set to today on every entry — signals fresh content to Google.
  - noindex / dup-canonical pages are excluded.
  - Existing priority + changefreq are preserved when present, otherwise
    sensible defaults are computed by page kind.

Usage:
  python refresh_sitemap.py            # dry-run (writes sitemap.new.xml)
  python refresh_sitemap.py --apply    # overwrite sitemap.xml
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from datetime import date
from pathlib import Path

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

ROOT = Path(__file__).resolve().parent
SITE = 'https://www.amaximumconstruction.com'

import site_audit  # reuse discovery + indexability logic
import restructure_hubs as rh  # reuse hub list + classifier


def page_priority(url: str) -> tuple[str, str]:
    """Return (priority, changefreq) for a URL based on classification."""
    if url == '/':
        return ('1.0', 'weekly')

    name = url.strip('/')
    if '/' not in name and name in rh.HUB_DIRS:
        return ('0.9', 'weekly')

    # blog/* posts
    if name.startswith('blog/'):
        return ('0.6', 'monthly')

    # Top-level slug — try to classify as location.
    if '/' not in name:
        kind, _hub, _city, _pi = rh.classify_dir(name)
        if kind == 'location':
            return ('0.8', 'monthly')
        # treat the rest as blog-ish content
        return ('0.6', 'monthly')

    # /locations/{city}/, /services/{x}/ — supporting pages
    if name.startswith('locations/'):
        return ('0.7', 'monthly')
    if name.startswith('services/'):
        return ('0.8', 'monthly')

    return ('0.6', 'monthly')


def parse_existing(sitemap_path: Path) -> dict[str, tuple[str, str]]:
    """Map URL path -> (priority, changefreq) from existing sitemap."""
    out: dict[str, tuple[str, str]] = {}
    if not sitemap_path.exists():
        return out
    text = sitemap_path.read_text(encoding='utf-8')
    for blk in re.findall(r'<url>(.*?)</url>', text, re.DOTALL):
        loc_m = re.search(r'<loc>\s*([^<\s]+)\s*</loc>', blk)
        if not loc_m:
            continue
        loc = loc_m.group(1)
        if not loc.startswith(SITE):
            continue
        url = loc[len(SITE):]
        prio = re.search(r'<priority>\s*([0-9.]+)\s*</priority>', blk)
        freq = re.search(r'<changefreq>\s*(\w+)\s*</changefreq>', blk)
        out[url] = (
            prio.group(1) if prio else '',
            freq.group(1) if freq else '',
        )
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='Overwrite sitemap.xml.')
    args = ap.parse_args(argv)

    pages = site_audit.discover_pages()
    existing = parse_existing(ROOT / 'sitemap.xml')

    today = date.today().isoformat()
    indexable: list[tuple[str, str, str]] = []  # (url, priority, changefreq)

    skipped_noindex = 0
    for url, p in pages:
        # Skip booking forms.
        if p.parent == ROOT and p.name in site_audit.NOINDEX_OK:
            continue
        # Read once for noindex check.
        html = p.read_text(encoding='utf-8', errors='replace')
        robots_m = site_audit.ROBOTS_META_RE.search(html)
        if robots_m and 'noindex' in robots_m.group(1).lower():
            skipped_noindex += 1
            continue
        prio, freq = page_priority(url)
        # Preserve existing values when set.
        old = existing.get(url)
        if old:
            if old[0]:
                prio = old[0]
            if old[1]:
                freq = old[1]
        indexable.append((url, prio, freq))

    indexable.sort(key=lambda x: x[0])

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url, prio, freq in indexable:
        lines.append('  <url>')
        lines.append(f'    <loc>{SITE}{url}</loc>')
        lines.append(f'    <changefreq>{freq}</changefreq>')
        lines.append(f'    <lastmod>{today}</lastmod>')
        lines.append(f'    <priority>{prio}</priority>')
        lines.append('  </url>')
    lines.append('</urlset>')
    new_xml = '\n'.join(lines) + '\n'

    target = ROOT / ('sitemap.xml' if args.apply else 'sitemap.new.xml')
    target.write_bytes(new_xml.encode('utf-8'))

    existing_urls = set(existing.keys())
    new_urls = {u for u, _, _ in indexable}
    added = sorted(new_urls - existing_urls)
    removed = sorted(existing_urls - new_urls)

    print(f'Discovered indexable pages: {len(indexable)}')
    print(f'Existing sitemap URLs:      {len(existing)}')
    print(f'Skipped (noindex):          {skipped_noindex}')
    print(f'Added:                      {len(added)}')
    print(f'Removed:                    {len(removed)}')
    print(f'Output:                     {target.name}')
    if added:
        print('\n+ Added:')
        for u in added:
            print(f'  + {u}')
    if removed:
        print('\n- Removed:')
        for u in removed:
            print(f'  - {u}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
