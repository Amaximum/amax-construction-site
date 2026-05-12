"""
Fix indexability site-wide:
1. Add <link rel="canonical"> to pages that lack one (insert into <head>).
2. Add missing pages to sitemap.xml (locations, book-now, sitemap), excluding
   pages whose canonical points to a different URL (duplicate dirs).
3. Skip thank-you-page (post-conversion).
4. Do NOT touch pages that already have a canonical pointing elsewhere
   (intentional duplicates).
"""
from __future__ import annotations
import os, re, datetime
from pathlib import Path

ROOT = Path(__file__).parent
HOST = "https://amaximumconstruction.com"
SITEMAP = ROOT / "sitemap.xml"
EXCLUDE_DIRS = {".git", "node_modules", ".venv", "__pycache__"}

# Pages that should never appear in sitemap (post-conversion / utility).
SITEMAP_EXCLUDE = {"/thank-you-page/"}


def find_pages() -> list[tuple[str, Path]]:
    out: list[tuple[str, Path]] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        if "index.html" not in filenames:
            continue
        rel_dir = Path(dirpath).relative_to(ROOT).as_posix()
        url = "/" if rel_dir == "." else "/" + rel_dir + "/"
        out.append((url, Path(dirpath) / "index.html"))
    return sorted(out)


CANON_RE = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"', re.I)


def get_canonical(text: str) -> str | None:
    m = CANON_RE.search(text)
    return m.group(1) if m else None


def insert_canonical(text: str, url: str) -> str:
    """Insert canonical link tag into <head> right before </head>."""
    tag = f'  <link rel="canonical" href="{url}">\n'
    # Try inserting after the existing meta description, otherwise before </head>
    if "</head>" in text:
        return text.replace("</head>", tag + "</head>", 1)
    return text  # no head — leave unchanged


def main() -> None:
    pages = find_pages()
    sitemap_text = SITEMAP.read_text(encoding="utf-8")
    existing_locs = set(re.findall(r"<loc>(.*?)</loc>", sitemap_text))

    added_canonical: list[str] = []
    to_add_to_sitemap: list[str] = []

    for url, file in pages:
        expected = HOST + url
        text = file.read_text(encoding="utf-8", errors="ignore")
        cur = get_canonical(text)

        # 1) Add canonical when missing.
        if cur is None:
            new_text = insert_canonical(text, expected)
            file.write_bytes(new_text.encode("utf-8"))
            added_canonical.append(url)
            cur = expected  # refresh for subsequent logic

        # 2) Decide sitemap inclusion.
        if url in SITEMAP_EXCLUDE:
            continue
        # Skip if canonical points elsewhere (duplicate page).
        if cur != expected:
            continue
        if expected in existing_locs:
            continue
        to_add_to_sitemap.append(expected)

    # 3) Patch sitemap.xml: insert new <url> entries before </urlset>.
    if to_add_to_sitemap:
        today = datetime.date.today().isoformat()
        block = "".join(
            f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n"
            for u in to_add_to_sitemap
        )
        sitemap_text = sitemap_text.replace("</urlset>", block + "</urlset>", 1)
        SITEMAP.write_bytes(sitemap_text.encode("utf-8"))

    print(f"Added canonical to: {len(added_canonical)} pages")
    for u in added_canonical:
        print("  +canonical", u)
    print(f"Added to sitemap:   {len(to_add_to_sitemap)} pages")
    for u in to_add_to_sitemap:
        print("  +sitemap  ", u)


if __name__ == "__main__":
    main()
