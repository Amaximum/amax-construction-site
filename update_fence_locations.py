#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parent

# All fence-contractor locations except the Richmond Hill reference page.
TARGETS = [
    "fence-contractor-in-aurora",
    "fence-contractor-in-east-york",
    "fence-contractor-in-etobicoke",
    "fence-contractor-in-markham",
    "fence-contractor-in-newmarket",
    "fence-contractor-in-north-york",
    "fence-contractor-in-scarborough",
    "fence-contractor-in-toronto",
    "fence-contractor-in-vaughan",
    "fence-contractor-in-woodbridge",
]

CITY_BY_SLUG = {
    "fence-contractor-in-aurora": "Aurora",
    "fence-contractor-in-east-york": "East York",
    "fence-contractor-in-etobicoke": "Etobicoke",
    "fence-contractor-in-markham": "Markham",
    "fence-contractor-in-newmarket": "Newmarket",
    "fence-contractor-in-north-york": "North York",
    "fence-contractor-in-scarborough": "Scarborough",
    "fence-contractor-in-toronto": "Toronto",
    "fence-contractor-in-vaughan": "Vaughan",
    "fence-contractor-in-woodbridge": "Woodbridge",
}


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def keyword_cluster(city: str) -> list[str]:
    return [
        f"fence contractor {city}",
        f"fence installation {city}",
        f"fence repair {city}",
        f"residential fencing {city}",
        f"commercial fencing {city}",
        f"wood privacy fence {city}",
        f"vinyl fence {city}",
        f"aluminum fence {city}",
        f"chain link fence {city}",
        f"composite fence {city}",
        f"custom fence design {city}",
        f"fence replacement {city}",
        f"fence gate installation {city}",
        f"pool fence {city}",
        f"bylaw-compliant fence {city}",
        f"licensed fence contractor {city}",
        f"insured fence company {city}",
        f"fence quote {city}",
        f"backyard privacy fence {city}",
        f"local fence builders {city}",
    ]


def keyword_paragraph(city: str) -> str:
    terms = ", ".join([f"<strong>{k}</strong>" for k in keyword_cluster(city)])
    return (
        "<p><strong>Local keyword cluster we cover in real projects:</strong> "
        f"{terms}.</p>"
    )


def update_head(html: str, h1_html: str, city: str) -> str:
    h1_text = strip_tags(h1_html)
    long_title = f"{h1_text} | aMaximum Construction"
    if len(long_title) <= 70:
        new_title = long_title
    else:
        # Keep title aligned with H1 while respecting SERP-safe length.
        h1_core = h1_text.split(" - ")[0].strip()
        new_title = f"{h1_core} | aMaximum Construction"

    new_desc = (
        f"Professional fence installation in {city} - wood, vinyl, aluminum, "
        f"and chain-link fencing. Licensed, insured contractors. Free quote "
        f"from aMaximum Construction."
    )

    html = re.sub(r"<title>.*?</title>", f"<title>{new_title}</title>", html, count=1, flags=re.DOTALL)

    html = re.sub(
        r'(<meta\s+[^>]*name=["\']description["\'][^>]*content=["\']).*?(["\'])',
        rf"\1{new_desc}\2",
        html,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )

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
    html = re.sub(
        r'(<meta\s+[^>]*property=["\']og:description["\'][^>]*content=["\']).*?(["\'])',
        rf"\1{new_desc}\2",
        html,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    html = re.sub(
        r'(<meta\s+[^>]*name=["\']twitter:description["\'][^>]*content=["\']).*?(["\'])',
        rf"\1{new_desc}\2",
        html,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return html


def inject_keywords_after_hero(html: str, city: str) -> str:
    if "Local keyword cluster we cover in real projects:" in html:
        return html

    para = keyword_paragraph(city)
    m = re.search(r"(<h1[^>]*>.*?</h1>\s*<p>.*?</p>)", html, flags=re.DOTALL | re.IGNORECASE)
    if not m:
        return html
    return html[: m.end()] + "\n" + para + html[m.end() :]


def process_slug(slug: str) -> bool:
    path = ROOT / slug / "index.html"
    if not path.exists():
        print(f"[miss] {slug}")
        return False

    city = CITY_BY_SLUG[slug]
    src = path.read_text(encoding="utf-8")

    h1_match = re.search(r"<h1[^>]*>.*?</h1>", src, flags=re.DOTALL | re.IGNORECASE)
    if not h1_match:
        print(f"[skip] {slug} no h1")
        return False

    out = src
    out = update_head(out, h1_match.group(0), city)
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
