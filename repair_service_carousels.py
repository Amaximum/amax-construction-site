from __future__ import annotations

import re
from pathlib import Path

from add_service_carousels import (
    ROOT,
    build_spec,
    detect_service_key,
    insert_after_page_hero,
    is_service_page,
    render_carousel,
)


SERVICE_GALLERY_RE = re.compile(
    r"<section\b[^>]*\bid=(\"|')service-gallery\1[^>]*>[\s\S]*?</section>",
    flags=re.IGNORECASE,
)


def iter_html_files() -> list[Path]:
    files: list[Path] = []
    for p in ROOT.rglob("*.html"):
        if not p.is_file():
            continue
        if "\\services\\" in str(p).lower():
            continue
        files.append(p)
    return files


def main() -> None:
    updated = 0
    inserted = 0
    skipped = 0

    for path in iter_html_files():
        html = path.read_text(encoding="utf-8", errors="ignore")
        if not is_service_page(html):
            continue

        key = detect_service_key(path, html)
        if not key:
            skipped += 1
            continue

        spec = build_spec(key)
        desired = render_carousel(spec).strip()

        m = SERVICE_GALLERY_RE.search(html)
        if m:
            current = m.group(0).strip()
            if current == desired:
                continue
            new_html = html[: m.start()] + desired + "\n" + html[m.end() :]
            path.write_text(new_html, encoding="utf-8")
            updated += 1
            continue

        # Missing gallery: insert (keeps placement consistent with other pages)
        new_html, did = insert_after_page_hero(html, desired + "\n")
        if did:
            path.write_text(new_html, encoding="utf-8")
            inserted += 1
        else:
            skipped += 1

    print("=== repair_service_carousels ===")
    print(f"Root: {ROOT}")
    print(f"Updated existing galleries: {updated}")
    print(f"Inserted missing galleries: {inserted}")
    print(f"Skipped (no key / no insert point): {skipped}")


if __name__ == "__main__":
    main()
