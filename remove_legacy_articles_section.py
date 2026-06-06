"""Remove legacy `<section ... id="articles">...</section>` related-articles
block from hub pages that also carry the canonical `id="related-articles"`
section produced by restructure_hubs.py. This eliminates the duplicate
blogs card on hub pages.

Usage: python remove_legacy_articles_section.py [--apply]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

SECTION_RE = re.compile(
    r'<section\b[^>]*\bid="articles"[^>]*>.*?</section>\s*',
    re.IGNORECASE | re.DOTALL,
)
HAS_RELATED_RE = re.compile(r'\bid="related-articles"', re.IGNORECASE)
HAS_LEGACY_RE = re.compile(r'\bid="articles"', re.IGNORECASE)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args(argv)
    apply = bool(args.apply)

    changed: list[tuple[str, int]] = []
    skipped_no_legacy: list[str] = []
    skipped_no_canonical: list[str] = []

    for index in sorted(ROOT.glob('*/index.html')):
        rel = index.relative_to(ROOT).as_posix()
        try:
            html = index.read_text(encoding='utf-8')
        except Exception:
            continue
        if not HAS_LEGACY_RE.search(html):
            continue
        if not HAS_RELATED_RE.search(html):
            skipped_no_canonical.append(rel)
            continue

        new_html, n = SECTION_RE.subn('', html)
        if n == 0:
            skipped_no_legacy.append(rel)
            continue

        changed.append((rel, n))
        if apply:
            index.write_bytes(new_html.encode('utf-8'))

    print('=' * 80)
    print(f'REMOVE LEGACY id="articles"  apply={apply}')
    print('=' * 80)
    print(f'\nWould remove from {len(changed)} hub page(s):')
    for rel, n in changed:
        print(f'  - {rel}  ({n} block)')
    if skipped_no_canonical:
        print(f'\nSkipped (no canonical id="related-articles"): {len(skipped_no_canonical)}')
        for rel in skipped_no_canonical:
            print(f'  ? {rel}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
