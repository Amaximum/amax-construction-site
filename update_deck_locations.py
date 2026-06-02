#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parent

TARGETS = [
    "deck-builder-gta",
    "deck-builder-schomberg",
    "deck-builder-toronto",
    "deck-contractor-aurora",
    "deck-contractor-bradford",
    "deck-contractor-burlington",
    "deck-contractor-concord",
    "deck-contractor-east-gwillimbury",
    "deck-contractor-east-york",
    "deck-contractor-etobicoke",
    "deck-contractor-hamilton",
    "deck-contractor-in-thornhill",
    "deck-contractor-king-city",
    "deck-contractor-kleinburg",
    "deck-contractor-north-york",
    "deck-contractor-scarborough",
    "deck-contractor-vaughan",
    "deck-contractor-woodbridge",
]

CITY_BY_SLUG = {
    "deck-builder-gta": "GTA",
    "deck-builder-schomberg": "Schomberg",
    "deck-builder-toronto": "Toronto",
    "deck-contractor-aurora": "Aurora",
    "deck-contractor-bradford": "Bradford",
    "deck-contractor-burlington": "Burlington",
    "deck-contractor-concord": "Concord",
    "deck-contractor-east-gwillimbury": "East Gwillimbury",
    "deck-contractor-east-york": "East York",
    "deck-contractor-etobicoke": "Etobicoke",
    "deck-contractor-hamilton": "Hamilton",
    "deck-contractor-in-thornhill": "Thornhill",
    "deck-contractor-king-city": "King City",
    "deck-contractor-kleinburg": "Kleinburg",
    "deck-contractor-north-york": "North York",
    "deck-contractor-scarborough": "Scarborough",
    "deck-contractor-vaughan": "Vaughan",
    "deck-contractor-woodbridge": "Woodbridge",
}


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def keywords(city: str) -> list[str]:
    return [
        f"deck builder {city}",
        f"deck contractor {city}",
        f"custom deck builder {city}",
        f"deck construction {city}",
        f"deck installation {city}",
        f"deck repair {city}",
        f"composite decking {city}",
        f"pressure treated deck {city}",
        f"cedar deck builder {city}",
        f"PVC decking {city}",
        f"multi-level deck {city}",
        f"deck railing installation {city}",
        f"permit-ready deck builder {city}",
        f"licensed deck contractor {city}",
        f"insured deck builder {city}",
        f"backyard deck design {city}",
        f"outdoor living deck {city}",
        f"low-maintenance deck {city}",
        f"deck quote {city}",
        f"local deck company {city}",
    ]


def keyword_paragraph(city: str) -> str:
    cluster = ", ".join([f"<strong>{k}</strong>" for k in keywords(city)])
    return (
        "<p><strong>Local keyword cluster we cover in real projects:</strong> "
        f"{cluster}.</p>"
    )


def update_head(html: str, h1_html: str) -> str:
    h1_text = strip_tags(h1_html)
    new_title = f"{h1_text} | aMaximum Construction"

    html = re.sub(r"<title>.*?</title>", f"<title>{new_title}</title>", html, count=1, flags=re.DOTALL)

    html = re.sub(
        r'(<meta\s+property=["\']og:title["\']\s+content=["\']).*?(["\']\s*/?>)',
        rf"\1{new_title}\2",
        html,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    html = re.sub(
        r'(<meta\s+name=["\']twitter:title["\']\s+content=["\']).*?(["\']\s*/?>)',
        rf"\1{new_title}\2",
        html,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return html


def inject_keywords_after_hero(html: str, city: str) -> str:
    para = keyword_paragraph(city)

    # Prevent duplicate injection when re-running.
    if "Local keyword cluster we cover in real projects:" in html:
        return html

    pat = re.compile(r"(<h1>.*?</h1>\s*<p>.*?</p>)", flags=re.DOTALL)
    m = pat.search(html)
    if not m:
        return html

    return html[: m.end()] + "\n" + para + html[m.end() :]


def process_slug(slug: str) -> bool:
    city = CITY_BY_SLUG[slug]
    path = ROOT / slug / "index.html"
    if not path.exists():
        print(f"[miss] {slug}")
        return False

    src = path.read_text(encoding="utf-8")

    h1_match = re.search(r"<h1>.*?</h1>", src, flags=re.DOTALL)
    if not h1_match:
        print(f"[skip] {slug} no h1")
        return False

    out = src
    out = update_head(out, h1_match.group(0))
    out = inject_keywords_after_hero(out, city)

    if out == src:
        print(f"[skip] {slug} no changes")
        return False

    path.write_text(out, encoding="utf-8")
    print(f"[ok]   {slug}")
    return True


def main() -> None:
    updated = 0
    for slug in TARGETS:
        if process_slug(slug):
            updated += 1
    print(f"Done. {updated}/{len(TARGETS)} updated.")


if __name__ == "__main__":
    main()
