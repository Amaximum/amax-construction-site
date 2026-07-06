"""site_audit.py

Comprehensive site-wide audit:
  - Indexability: robots meta noindex, canonical presence
  - SEO basics: exactly one H1, H1 keywords appear in <title>
  - Sitemap membership: every indexable page is present in sitemap.xml
  - Reports per-issue with category counts.

Read-only; does not modify anything.

Usage:
  python site_audit.py
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path
from html import unescape

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

ROOT = Path(__file__).resolve().parent
SITE = 'https://amaximumconstruction.com'

# Pages that are intentionally non-indexable (forms, thank-you pages, drafts).
NOINDEX_OK = {
    'book-basement.html', 'book-bathroom.html', 'book-canopy.html',
    'book-carpentry.html', 'book-christmas.html', 'book-contractor.html',
    'book-deck.html', 'book-demolition.html', 'book-electrical.html',
    'book-excavation.html', 'book-fence.html', 'book-handy.html',
    'book-interlock.html', 'book-landscaping.html', 'book-painting.html',
    'book-plumbing.html', 'book-railing.html', 'book-renovation.html',
    'thank-you.html',
}

# Files we should not consider as "pages" at all.
SKIP_FILES = {
    '404.html', 'index-seo-2026.html',
}

H1_RE = re.compile(r'<h1\b[^>]*>(.*?)</h1>', re.I | re.S)
TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.I | re.S)
CANONICAL_RE = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"', re.I)
ROBOTS_META_RE = re.compile(r'<meta\s+name="robots"\s+content="([^"]+)"', re.I)
TAG_RE = re.compile(r'<[^>]+>')
WS_RE = re.compile(r'\s+')


def read(p: Path) -> str:
    return p.read_text(encoding='utf-8', errors='replace')


def strip_tags(html: str) -> str:
    return WS_RE.sub(' ', unescape(TAG_RE.sub(' ', html))).strip()


def discover_pages() -> list[tuple[str, Path]]:
    """Yield (url_path, file_path). url_path starts with '/' and ends with '/' for
    directory pages, or is the file path for top-level *.html."""
    pages: list[tuple[str, Path]] = []

    for p in sorted(ROOT.glob('*.html')):
        if p.name in SKIP_FILES:
            continue
        url = '/' if p.name == 'index.html' else f'/{p.name}'
        pages.append((url, p))

    skip_dirs = {'css', 'js', 'images', 'img', 'fonts', 'assets', 'admin',
                 'cgi-bin', '__pycache__', '.venv', '.git', 'node_modules',
                 'forms', 'data'}

    for d in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        if d.name.startswith('.') or d.name in skip_dirs:
            continue
        for idx in sorted(d.rglob('index.html')):
            rel = idx.parent.relative_to(ROOT).as_posix()
            url = f'/{rel}/'
            pages.append((url, idx))

    return pages


def parse_sitemap(sitemap_path: Path) -> set[str]:
    if not sitemap_path.exists():
        return set()
    text = sitemap_path.read_text(encoding='utf-8')
    locs = re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', text)
    out: set[str] = set()
    for loc in locs:
        if loc.startswith(SITE):
            out.add(loc[len(SITE):])
        else:
            out.add(loc)
    return out


def keyword_overlap(title: str, h1: str) -> tuple[bool, set[str]]:
    """Return (overlap_ok, missing_words). H1 must share >=1 significant word
    with title (or H1 should be substring of title or vice versa)."""
    stop = {'and', 'the', 'for', 'with', 'your', 'in', 'of', 'a', 'an', 'to',
            'on', 'at', 'is', 'are', 'by', 'from', '&', '|', '-', 'gta', '\u2014'}
    def words(s: str) -> set[str]:
        return {w for w in re.findall(r"[a-z][a-z0-9'-]+", s.lower())
                if w not in stop and len(w) > 2}
    tw, hw = words(title), words(h1)
    if not hw:
        return (False, set())
    overlap = hw & tw
    return (bool(overlap), hw - tw)


def audit_page(url: str, p: Path) -> dict:
    html = read(p)
    title_m = TITLE_RE.search(html)
    title_raw = strip_tags(title_m.group(1)) if title_m else ''
    h1s = H1_RE.findall(html)
    h1_texts = [strip_tags(h) for h in h1s]
    canonical_m = CANONICAL_RE.search(html)
    canonical = canonical_m.group(1) if canonical_m else ''
    robots_m = ROBOTS_META_RE.search(html)
    robots = robots_m.group(1).strip() if robots_m else ''

    issues: list[str] = []
    is_form = p.name in NOINDEX_OK
    has_noindex = 'noindex' in robots.lower()

    if is_form:
        if not has_noindex:
            issues.append('FORM-not-noindex')
    else:
        if has_noindex:
            issues.append('PAGE-noindex')
        if not canonical:
            issues.append('missing-canonical')
        else:
            expected = SITE + url
            if canonical.rstrip('/') != expected.rstrip('/'):
                issues.append(f'canonical-mismatch (got {canonical})')

    if len(h1_texts) == 0:
        issues.append('no-H1')
    elif len(h1_texts) > 1:
        issues.append(f'multiple-H1 ({len(h1_texts)})')

    if not title_raw:
        issues.append('no-title')

    if h1_texts and title_raw:
        ok, _missing = keyword_overlap(title_raw, h1_texts[0])
        if not ok:
            issues.append('h1-not-in-title')

    return {
        'url': url,
        'path': str(p.relative_to(ROOT)),
        'title': title_raw,
        'h1': h1_texts[0] if h1_texts else '',
        'h1_count': len(h1_texts),
        'canonical': canonical,
        'robots': robots,
        'is_form': is_form,
        'issues': issues,
    }


def main() -> int:
    pages = discover_pages()
    sitemap_urls = parse_sitemap(ROOT / 'sitemap.xml')

    results = [audit_page(url, p) for url, p in pages]

    print(f'Total pages discovered: {len(results)}')
    print(f'Sitemap URLs:           {len(sitemap_urls)}')
    print()

    by_issue: dict[str, list[dict]] = {}
    for r in results:
        for code in r['issues']:
            key = code.split(' ')[0]
            by_issue.setdefault(key, []).append(r)

    indexable = [r for r in results if not r['is_form']]
    in_sitemap = [r for r in indexable if r['url'] in sitemap_urls]
    not_in_sitemap = [r for r in indexable if r['url'] not in sitemap_urls]

    sitemap_orphans = sitemap_urls - {r['url'] for r in indexable}

    print('========== ISSUE SUMMARY ==========')
    for code in sorted(by_issue):
        print(f'  {code:<25} {len(by_issue[code])}')
    print(f'  {"missing-from-sitemap":<25} {len(not_in_sitemap)}')
    print(f'  {"sitemap-orphan-urls":<25} {len(sitemap_orphans)}')
    print()

    print('========== DETAIL ==========')
    for code in sorted(by_issue):
        rows = by_issue[code]
        print(f'\n--- {code} ({len(rows)}) ---')
        for r in rows[:50]:
            extra = ''
            if code == 'multiple-H1':
                extra = f' h1_count={r["h1_count"]}'
            elif code == 'canonical-mismatch':
                extra = f' canonical={r["canonical"]}'
            elif code == 'h1-not-in-title':
                extra = f' | T="{r["title"][:70]}" | H1="{r["h1"][:60]}"'
            print(f'  {r["url"]:<70}{extra}')
        if len(rows) > 50:
            print(f'  ... and {len(rows) - 50} more')

    print(f'\n--- missing-from-sitemap ({len(not_in_sitemap)}) ---')
    for r in not_in_sitemap[:50]:
        print(f'  {r["url"]}')
    if len(not_in_sitemap) > 50:
        print(f'  ... and {len(not_in_sitemap) - 50} more')

    print(f'\n--- sitemap-orphan-urls ({len(sitemap_orphans)}) ---')
    for u in sorted(sitemap_orphans)[:50]:
        print(f'  {u}')
    if len(sitemap_orphans) > 50:
        print(f'  ... and {len(sitemap_orphans) - 50} more')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
