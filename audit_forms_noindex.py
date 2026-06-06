"""Audit all form-bearing pages for noindex."""
from __future__ import annotations
import io, re, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

ROOT = Path(__file__).resolve().parent
ROBOTS_RE = re.compile(r'<meta\s+name="robots"\s+content="([^"]+)"', re.I)
FORM_RE = re.compile(r'<form\b', re.I)
CANON_RE = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"', re.I)
TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.I | re.S)
H1_RE = re.compile(r'<h1\b[^>]*>(.*?)</h1>', re.I | re.S)

SKIP_DIRS = {'.git', '.venv', 'node_modules', '__pycache__',
             'css', 'js', 'images', 'img', 'fonts', 'assets'}

def discover() -> list[Path]:
    out: list[Path] = []
    for p in ROOT.rglob('*.html'):
        rel = p.relative_to(ROOT).parts
        if any(d in SKIP_DIRS for d in rel):
            continue
        out.append(p)
    return sorted(out)

def main() -> int:
    book_pages: list[tuple[Path, str, bool]] = []
    other_form_pages: list[tuple[Path, str, bool]] = []

    for p in discover():
        try:
            text = p.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        has_form = bool(FORM_RE.search(text))
        if not has_form and not p.name.startswith('book-') and 'thank-you' not in p.name:
            continue
        rm = ROBOTS_RE.search(text)
        robots = rm.group(1).lower() if rm else ''
        is_noindex = 'noindex' in robots
        rel = p.relative_to(ROOT).as_posix()
        if p.name.startswith('book-') or 'thank-you' in p.name or 'book-now' in rel:
            book_pages.append((p, robots, is_noindex))
        else:
            other_form_pages.append((p, robots, is_noindex))

    def fmt(rows):
        for p, robots, ni in rows:
            mark = 'OK' if ni else 'WARN'
            rel = p.relative_to(ROOT).as_posix()
            print(f'  [{mark:<4}] {rel:<55} robots="{robots or "(none)"}"')

    print(f'=== Booking / thank-you pages ({len(book_pages)}) ===')
    fmt(book_pages)
    bad_books = [r for r in book_pages if not r[2]]
    print(f'\n=== Other pages with <form> tag ({len(other_form_pages)}) ===')
    fmt(other_form_pages)
    bad_other_indexed = [r for r in other_form_pages if not r[2]]

    print('\n----- summary -----')
    print(f'booking/thank-you total:       {len(book_pages)}')
    print(f'  noindex correct:             {len(book_pages) - len(bad_books)}')
    print(f'  MISSING noindex (bad):       {len(bad_books)}')
    print(f'other pages with <form>:       {len(other_form_pages)}')
    print(f'  noindex (forms-only pages):  {len(other_form_pages) - len(bad_other_indexed)}')
    print(f'  indexable (likely OK):       {len(bad_other_indexed)}  (these are content pages with embedded forms)')
    return 0 if not bad_books else 1

if __name__ == '__main__':
    raise SystemExit(main())
