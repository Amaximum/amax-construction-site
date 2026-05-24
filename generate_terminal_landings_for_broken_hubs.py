"""Generate service-in-city terminal pages for hubs that currently have broken
location-card links pointing to /locations/<city>/.

For each (hub, city) pair we:
1. Read the hub's index.html.
2. Replace title / meta / canonical / schema / h1 / hero intro to be city-aware.
3. Strip the "service-areas" cross-location block (no cross-location links on a
   terminal page) and the "related articles" block (no cross-service links).
4. Write to <new-slug>-in-<city>/index.html.
5. Update the hub's `.location-card` href to point to the new page.

Idempotent: skips writing pages that already exist; only updates hub links
that still point at /locations/<city>/ in a `.location-card`.

Run from repo root:
    python generate_terminal_landings_for_broken_hubs.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOMAIN = "https://amaximumconstruction.com"

# Hub slug -> per-city target slug pattern + display name + booking page +
# hero-intro replacement template + image preload hint.
HUBS: dict[str, dict[str, str]] = {
    "electrical-handyman-services": {
        "display": "Electrical Handyman Services",
        "service_short": "Electrical Services",
        "new_slug": "electrical-services-in-{city_slug}",
        "title_template": "Electrical Services in {city} | Licensed Electricians",
        "meta_template": "Licensed electrical services in {city}. Panel upgrades, EV chargers, lighting, outlets, and renovation rough-ins. ESA permits pulled. Free quotes from aMaximum Construction.",
        "hero_paragraph": "aMaximum Construction provides licensed electrical work for homeowners in {city}. Panel upgrades, EV charger installation, lighting, outlets, and renovation rough-ins — completed to the Ontario Electrical Safety Code with ESA permits where required.",
    },
    "handyman-plumbing-services": {
        "display": "Plumbing Services",
        "service_short": "Plumbing Services",
        "new_slug": "plumbing-services-in-{city_slug}",
        "title_template": "Plumbing Services in {city} | Licensed Plumbers",
        "meta_template": "Licensed plumbing services in {city}. Faucet, toilet, and fixture replacement, leak repair, drain clearing, and rough-in plumbing. Free quotes from aMaximum Construction.",
        "hero_paragraph": "aMaximum Construction handles plumbing work for homeowners in {city}. Faucet and fixture replacement, leak repair, drain clearing, and rough-in plumbing — pressure-tested and clean on completion.",
    },
    "handyman-painting-services": {
        "display": "Painting Services",
        "service_short": "Painting Services",
        "new_slug": "painting-services-in-{city_slug}",
        "title_template": "Painting Services in {city} | Interior & Exterior",
        "meta_template": "Interior and exterior painting services in {city}. Wall, ceiling, trim, door, and full-room repaint with proper prep and durable finishes. Free quotes from aMaximum Construction.",
        "hero_paragraph": "aMaximum Construction provides interior and exterior painting in {city}. Walls, ceilings, trim, doors, and full rooms — surfaces prepped, edges protected, and finishes applied to even coverage.",
    },
    "canopy": {
        "display": "Canopy Installation",
        "service_short": "Canopy Installation",
        "new_slug": "canopy-installation-in-{city_slug}",
        "title_template": "Canopy Installation in {city} | Patio & Deck Shade",
        "meta_template": "Custom canopy installation in {city}. Retractable, fixed, and motorized awnings for patios, decks, and entryways. Engineered for wind load. Free quotes from aMaximum Construction.",
        "hero_paragraph": "aMaximum Construction installs custom canopies and awnings for homeowners in {city}. Retractable, fixed, and motorized shade structures for patios, decks, and entryways — anchored for long-term wind load.",
    },
    "excavation-services": {
        "display": "Excavation Services",
        "service_short": "Excavation Services",
        "new_slug": "excavation-services-in-{city_slug}",
        "title_template": "Excavation Services in {city} | Foundations & Grading",
        "meta_template": "Excavation services in {city}. Foundation digs, footings, grading, trenching, and site prep with utility locates first. Free quotes from aMaximum Construction.",
        "hero_paragraph": "aMaximum Construction handles excavation for homeowners and contractors in {city}. Foundation digs, footings, grading, trenching, and site prep — utility locates always done before the first cut.",
    },
}

# Cities served by all 5 broken hubs.
CITIES = [
    ("Toronto", "toronto"),
    ("Markham", "markham"),
    ("Richmond Hill", "richmond-hill"),
    ("Vaughan", "vaughan"),
    ("Newmarket", "newmarket"),
]


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------


def _strip_block_by_id(html: str, section_id: str) -> str:
    """Remove a single <section ... id="<section_id>" ... > ... </section> block.

    Uses a small state machine to balance nested <section> tags.
    """
    open_re = re.compile(
        r'<section[^>]*\bid="' + re.escape(section_id) + r'"[^>]*>',
        flags=re.IGNORECASE,
    )
    open_match = open_re.search(html)
    if not open_match:
        return html

    section_open = re.compile(r"<section\b", re.IGNORECASE)
    section_close = re.compile(r"</section>", re.IGNORECASE)

    depth = 1
    pos = open_match.end()
    end_pos: int | None = None
    while pos < len(html):
        open_next = section_open.search(html, pos)
        close_next = section_close.search(html, pos)
        if close_next is None:
            break
        if open_next is not None and open_next.start() < close_next.start():
            depth += 1
            pos = open_next.end()
        else:
            depth -= 1
            pos = close_next.end()
            if depth == 0:
                end_pos = pos
                break

    if end_pos is None:
        return html
    return html[: open_match.start()] + html[end_pos:]


def _safe_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


# ---------------------------------------------------------------------------
# Per-hub generation.
# ---------------------------------------------------------------------------


def generate_for_hub(hub_slug: str, meta: dict[str, str]) -> tuple[int, int]:
    hub_path = ROOT / hub_slug / "index.html"
    if not hub_path.exists():
        print(f"  ! hub missing: {hub_slug}")
        return 0, 0

    hub_html = hub_path.read_text(encoding="utf-8")

    # Strip the cross-location and cross-service sections once — these are
    # excluded from every terminal page we generate.
    base_html = _strip_block_by_id(hub_html, "service-areas")
    base_html = _strip_block_by_id(base_html, "articles")

    created = 0
    skipped = 0

    for city_name, city_slug in CITIES:
        new_slug = meta["new_slug"].format(city_slug=city_slug)
        out_path = ROOT / new_slug / "index.html"
        if out_path.exists():
            skipped += 1
            continue

        new_url = f"{DOMAIN}/{new_slug}/"
        title = meta["title_template"].format(city=city_name)
        meta_desc = meta["meta_template"].format(city=city_name)
        hero_para = meta["hero_paragraph"].format(city=city_name)
        h1_new = f"{meta['display']} in {city_name}"

        page = base_html

        # 1. <title>
        page = re.sub(
            r"<title>.*?</title>",
            f"<title>{title}</title>",
            page,
            count=1,
            flags=re.DOTALL,
        )

        # 2. Standard meta description (the first <meta name="description" ...>).
        page = re.sub(
            r'<meta\s+content="[^"]*"\s+name="description"\s*/?>',
            f'<meta content="{meta_desc}" name="description"/>',
            page,
            count=1,
        )
        page = re.sub(
            r'<meta\s+name="description"\s+content="[^"]*"\s*/?>',
            f'<meta name="description" content="{meta_desc}">',
            page,
            count=1,
        )

        # 3. og:title / og:description / og:url
        page = re.sub(
            r'<meta\s+content="[^"]*"\s+property="og:title"\s*/?>',
            f'<meta content="{title}" property="og:title"/>',
            page,
            count=1,
        )
        page = re.sub(
            r'<meta\s+content="[^"]*"\s+property="og:description"\s*/?>',
            f'<meta content="{meta_desc}" property="og:description"/>',
            page,
            count=1,
        )
        page = re.sub(
            r'<meta\s+content="[^"]*"\s+property="og:url"\s*/?>',
            f'<meta content="{new_url}" property="og:url"/>',
            page,
            count=1,
        )

        # 4. twitter:title / twitter:description
        page = re.sub(
            r'<meta\s+name="twitter:title"\s+content="[^"]*"\s*/?>',
            f'<meta name="twitter:title" content="{title}">',
            page,
            count=1,
        )
        page = re.sub(
            r'<meta\s+name="twitter:description"\s+content="[^"]*"\s*/?>',
            f'<meta name="twitter:description" content="{meta_desc}">',
            page,
            count=1,
        )

        # 5. canonical (both possible attribute orders).
        page = re.sub(
            r'<link\s+href="[^"]*"\s+rel="canonical"\s*/?>',
            f'<link href="{new_url}" rel="canonical"/>',
            page,
            count=1,
        )
        page = re.sub(
            r'<link\s+rel="canonical"\s+href="[^"]*"\s*/?>',
            f'<link rel="canonical" href="{new_url}">',
            page,
            count=1,
        )

        # 6. LocalBusiness schema: url, addressLocality, areaServed.
        page = re.sub(
            r'("@type":\s*"LocalBusiness"[\s\S]*?"url":\s*)"[^"]*"',
            lambda m: f'{m.group(1)}"{new_url}"',
            page,
            count=1,
        )
        page = re.sub(
            r'"addressLocality":\s*"[^"]*"',
            f'"addressLocality": "{city_name}"',
            page,
            count=1,
        )
        page = re.sub(
            r'"areaServed":\s*\{"@type":\s*"City",\s*"name":\s*"[^"]*"\}',
            f'"areaServed": {{"@type": "City", "name": "{city_name}"}}',
            page,
            count=1,
        )

        # 7. Service schema: areaServed string + description.
        page = re.sub(
            r'("@type":\s*"Service"[\s\S]*?"areaServed":\s*)"[^"]*"',
            lambda m: f'{m.group(1)}"{city_name}, GTA"',
            page,
            count=1,
        )
        page = re.sub(
            r'("@type":\s*"Service"[\s\S]*?"description":\s*)"[^"]*"',
            lambda m: f'{m.group(1)}"{meta_desc}"',
            page,
            count=1,
        )

        # 8. BreadcrumbList: position 3 name + item.
        page = re.sub(
            r'("@type":\s*"BreadcrumbList"[\s\S]*?"position":\s*3,\s*"name":\s*)"[^"]*"(,\s*"item":\s*)"[^"]*"',
            lambda m: f'{m.group(1)}"{h1_new}"{m.group(2)}"{new_url}"',
            page,
            count=1,
        )

        # 9. H1 + first paragraph inside .page-hero.
        page = re.sub(
            r'(<div class="page-hero">\s*<h1>)[^<]*(</h1>\s*<p>)[^<]*(</p>)',
            lambda m: f'{m.group(1)}{h1_new}{m.group(2)}{hero_para}{m.group(3)}',
            page,
            count=1,
            flags=re.DOTALL,
        )

        _safe_write(out_path, page)
        created += 1

    return created, skipped


# ---------------------------------------------------------------------------
# Hub link rewrites.
# ---------------------------------------------------------------------------


def rewrite_hub_links(hub_slug: str, meta: dict[str, str]) -> int:
    hub_path = ROOT / hub_slug / "index.html"
    html = hub_path.read_text(encoding="utf-8")

    changed = 0
    for city_name, city_slug in CITIES:
        new_slug = meta["new_slug"].format(city_slug=city_slug)
        new_href = f"/{new_slug}/"

        # Match: <a class="location-card" href="/locations/<city>/">City</a>
        # We restrict to .location-card to avoid touching footer <li><a> links.
        pattern = re.compile(
            r'(<a[^>]*class="location-card"[^>]*\bhref=")/locations/'
            + re.escape(city_slug)
            + r'/(")',
        )
        new_html, n = pattern.subn(rf"\1{new_href}\2", html)
        if n:
            html = new_html
            changed += n

    if changed:
        hub_path.write_bytes(html.encode("utf-8"))
    return changed


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------


def main() -> None:
    total_created = 0
    total_skipped = 0
    total_links = 0
    for hub_slug, meta in HUBS.items():
        c, s = generate_for_hub(hub_slug, meta)
        link_count = rewrite_hub_links(hub_slug, meta)
        total_created += c
        total_skipped += s
        total_links += link_count
        print(
            f"  {hub_slug:40s} created={c:>2}  skipped={s:>2}  hub-links-updated={link_count}"
        )
    print()
    print(f"TOTAL: created={total_created}, skipped={total_skipped}, hub-links={total_links}")


if __name__ == "__main__":
    main()
