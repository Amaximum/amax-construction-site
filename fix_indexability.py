"""
Sitemap & canonical audit/fix:
1. Find all index.html pages on disk.
2. Find all <loc> in sitemap.xml.
3. Add any missing pages to sitemap.xml.
4. Verify each page has a canonical matching its on-disk URL (host without www).
5. Report mismatches and (optionally) fix.
"""
from __future__ import annotations
import os, re, datetime
from pathlib import Path

ROOT = Path(__file__).parent
HOST = "https://amaximumconstruction.com"
SITEMAP = ROOT / "sitemap.xml"

EXCLUDE_DIRS = {".git", "node_modules", ".venv", "__pycache__"}
# Top-level files that are not "page directories" but standalone HTML (book-*.html etc.)
SKIP_PAGES_REL = set()


def find_pages() -> list[str]:
    """Return list of site-relative URL paths (e.g. '/foo/' or '/') for every index.html."""
    pages: list[str] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # prune excluded dirs in-place
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        if "index.html" not in filenames:
            continue
        rel_dir = Path(dirpath).relative_to(ROOT).as_posix()
        if rel_dir == ".":
            url_path = "/"
        else:
            url_path = "/" + rel_dir + "/"
        pages.append(url_path)
    return sorted(pages)


def parse_sitemap() -> tuple[str, list[str]]:
    text = SITEMAP.read_text(encoding="utf-8")
    locs = re.findall(r"<loc>(.*?)</loc>", text)
    return text, locs


def canonical_of(file: Path) -> str | None:
    try:
        text = file.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    m = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', text)
    return m.group(1) if m else None


def main() -> None:
    pages = find_pages()
    sm_text, locs = parse_sitemap()
    loc_set = set(locs)

    # 1) Missing-from-sitemap report
    missing = []
    for p in pages:
        url = HOST + p
        if url not in loc_set:
            missing.append(url)

    # 2) Canonical audit
    bad_canonical: list[tuple[str, str | None]] = []
    for p in pages:
        expected = HOST + p
        f = ROOT / (p.strip("/") or ".") / "index.html"
        # Special: '/' -> ROOT/index.html
        if p == "/":
            f = ROOT / "index.html"
        cur = canonical_of(f)
        if cur != expected:
            bad_canonical.append((expected, cur))

    print(f"Pages on disk:  {len(pages)}")
    print(f"Sitemap <loc>:  {len(locs)}")
    print(f"Missing from sitemap: {len(missing)}")
    for m in missing[:50]:
        print("  -", m)
    if len(missing) > 50:
        print(f"  ... and {len(missing)-50} more")
    print(f"Bad/missing canonical: {len(bad_canonical)}")
    for exp, cur in bad_canonical[:30]:
        print(f"  - expected {exp} | current {cur!r}")
    if len(bad_canonical) > 30:
        print(f"  ... and {len(bad_canonical)-30} more")


if __name__ == "__main__":
    main()
