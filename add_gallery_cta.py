"""Add a 'Get a Free Quote' CTA button after the photo carousel on every page.

Logic:
- Find every page containing `<section id="service-gallery"` ... closing `</section>`.
- Skip if a CTA already follows directly (look for class `gallery-cta` marker).
- Detect the page's booking link from the nav `<a class="... nav-quote ..." href="...">BOOK NOW</a>`,
  or fall back to "/contact-us/".
- Inject CTA block right after the gallery `</section>`.

Idempotent: re-runs do nothing thanks to the `gallery-cta` marker.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).parent

MARKER = "gallery-cta"
CTA_TEMPLATE = (
    '\n<div class="shell {marker}" style="padding:16px 0 8px;text-align:center;">\n'
    '  <a class="btn btn-primary" href="{href}" style="display:inline-block;">Get a Free Quote &rarr;</a>\n'
    '</div>\n'
)

NAV_QUOTE_RE = re.compile(
    r'<a[^>]*\bclass="[^"]*\bnav-quote\b[^"]*"[^>]*\bhref="([^"]+)"',
    re.IGNORECASE,
)
NAV_QUOTE_RE_ALT = re.compile(
    r'<a[^>]*\bhref="([^"]+)"[^>]*\bclass="[^"]*\bnav-quote\b[^"]*"',
    re.IGNORECASE,
)

GALLERY_OPEN_RE = re.compile(
    r'<section\b[^>]*\bid="service-gallery"[^>]*>',
    re.IGNORECASE,
)

def find_gallery_close(html: str, open_end: int) -> int:
    """Return index just after the matching </section> for the gallery section."""
    depth = 1
    i = open_end
    section_open = re.compile(r'<section\b', re.IGNORECASE)
    section_close = re.compile(r'</section\s*>', re.IGNORECASE)
    while i < len(html):
        m_open = section_open.search(html, i)
        m_close = section_close.search(html, i)
        if not m_close:
            return -1
        if m_open and m_open.start() < m_close.start():
            depth += 1
            i = m_open.end()
        else:
            depth -= 1
            i = m_close.end()
            if depth == 0:
                return i
    return -1

def detect_book_href(html: str) -> str:
    m = NAV_QUOTE_RE.search(html) or NAV_QUOTE_RE_ALT.search(html)
    if m:
        return m.group(1)
    # Generic fallback: first /book-*.html link in document
    m2 = re.search(r'href="(/book-[a-z0-9\-]+\.html)"', html, re.IGNORECASE)
    if m2:
        return m2.group(1)
    return "/contact-us/"

def process_file(path: Path) -> bool:
    src = path.read_text(encoding="utf-8")
    m = GALLERY_OPEN_RE.search(src)
    if not m:
        return False
    close_end = find_gallery_close(src, m.end())
    if close_end == -1:
        return False
    # Skip if already injected (look at next ~600 chars after the gallery)
    tail = src[close_end:close_end + 600]
    if MARKER in tail:
        return False
    href = detect_book_href(src)
    cta = CTA_TEMPLATE.format(marker=MARKER, href=href)
    new_src = src[:close_end] + cta + src[close_end:]
    path.write_text(new_src, encoding="utf-8")
    return True

def main() -> None:
    changed = []
    skipped_with_gallery = 0
    for path in ROOT.rglob("index.html"):
        # Skip node_modules / .venv etc just in case
        parts = set(path.parts)
        if any(p in parts for p in (".venv", "node_modules", ".git")):
            continue
        try:
            head = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if 'id="service-gallery"' not in head:
            continue
        skipped_with_gallery += 1
        if process_file(path):
            changed.append(path)
    # Also check root-level HTML files
    for path in ROOT.glob("*.html"):
        try:
            head = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if 'id="service-gallery"' not in head:
            continue
        skipped_with_gallery += 1
        if process_file(path):
            changed.append(path)

    print(f"Pages with gallery: {skipped_with_gallery}")
    print(f"Updated: {len(changed)}")
    for p in changed:
        print(" -", p.relative_to(ROOT))

if __name__ == "__main__":
    main()
