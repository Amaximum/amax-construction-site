"""Sitewide funnel-closing pass.

Three passes:

PASS A — Strip cross-blocks from every TERMINAL page.
    A terminal page is any top-level <slug>/index.html that is NOT one of the
    service hubs, location hubs, or known info pages. On those pages we delete
    `<section id="service-areas">` (cross-location grid) and
    `<section id="articles">` (cross-service "Related Articles" grid).

PASS B — Fix service HUB `.location-card` links.
    For each of the 18 service hubs, any `.location-card` whose href starts
    with /locations/<city>/ is rewritten to the matching terminal page for
    that (service, city) pair if one exists.

PASS C — Fix location HUB service-card links.
    For each /locations/<city>/index.html, any service card whose href is
    `/<service-hub-slug>/` is rewritten to the matching terminal page for
    (that service, this city) if one exists.

The script is idempotent. Run from repo root:

    python sitewide_close_funnel.py
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# 1. Inventory.
# ---------------------------------------------------------------------------

SERVICE_HUBS: dict[str, str] = {
    # hub slug -> service category id
    "deck-builder": "deck",
    "deck-railings": "railing",
    "fence-installation": "fence",
    "bathroom-renovation": "bathroom",
    "basement-renovation": "basement",
    "handyman-plumbing-services": "plumbing",
    "canopy": "canopy",
    "landscaping-services": "landscaping",
    "general-contractor": "general-contractor",
    "handyman-services": "handyman",
    "interlocking-paver-services": "interlock",
    "carpenter-services": "carpentry",
    "electrical-handyman-services": "electrical",
    "handyman-painting-services": "painting",
    "demolition-services": "demolition",
    "excavation-services": "excavation",
    "home-renovation": "home-renovation",
    "christmas-lights-installation-toronto-gta": "christmas",
}

# Slug prefixes -> service category. Order matters (longest/most specific first).
TERMINAL_PREFIXES: list[tuple[str, str]] = [
    # christmas
    ("christmas-lights-installation-in-", "christmas"),
    ("christmas-lights-installation-", "christmas"),
    ("professional-christmas-lights-", "christmas"),
    # deck railing
    ("deck-railing-installer-in-", "railing"),
    ("deck-railing-installer-", "railing"),
    ("deck-railing-installation-in-", "railing"),
    ("deck-railing-builder-", "railing"),
    ("deck-railings-", "railing"),
    ("deck-railing-", "railing"),
    # deck
    ("deck-builder-in-", "deck"),
    ("deck-builder-", "deck"),
    ("deck-contractor-in-", "deck"),
    ("deck-contractor-", "deck"),
    ("custom-decks-", "deck"),
    # fence
    ("fence-contractor-in-", "fence"),
    ("fence-contractor-", "fence"),
    ("fence-installer-", "fence"),
    ("fence-installation-", "fence"),
    ("fence-services-", "fence"),
    # bathroom
    ("bathroom-renovation-", "bathroom"),
    ("bathrooms-renovation-", "bathroom"),
    # basement
    ("best-basement-renovation-service-in-", "basement"),
    ("best-basement-renovation-service-", "basement"),
    ("basement-and-bathroom-renovation-in-", "basement"),
    ("basement-bathroom-renovation-", "basement"),
    ("basement-renovation-", "basement"),
    # plumbing
    ("plumbing-services-in-", "plumbing"),
    # electrical
    ("electrical-services-in-", "electrical"),
    # painting
    ("painting-services-in-", "painting"),
    # canopy
    ("canopy-installation-in-", "canopy"),
    # excavation
    ("excavation-services-in-", "excavation"),
    # landscaping
    ("landscaping-services-", "landscaping"),
    # general contractor
    ("general-contractor-services-", "general-contractor"),
    ("general-contractor-in-", "general-contractor"),
    ("general-contractor-", "general-contractor"),
    # handyman
    ("handyman-service-in-", "handyman"),
    ("handyman-services-", "handyman"),
    # interlock
    ("interlocking-stone-services-in-", "interlock"),
    ("interlocking-stone-services-", "interlock"),
    ("interlock-paving-contractor-in-", "interlock"),
    ("interlock-paving-contractor-", "interlock"),
    # carpentry
    ("carpenter-services-", "carpentry"),
    # demolition
    ("demolition-service-in-", "demolition"),
    ("demolition-service-", "demolition"),
    ("demolition-services-", "demolition"),
    # home renovation
    ("home-renovation-in-", "home-renovation"),
    ("home-renovation-", "home-renovation"),
    ("renovation-services-in-", "home-renovation"),
    ("renovation-services-", "home-renovation"),
    ("renovation-service", "home-renovation"),
]

# Exact-match slugs (no city suffix) → service category.
EXACT_TERMINAL_SLUGS: dict[str, str] = {
    "general-contractor-services-near-me": "general-contractor",
    "1-basement-renovation-near-me": "basement",
    "paving-company": "interlock",
    "renovation-service": "home-renovation",
}

# Canonical city slug aliases (some pages drop the "the" / use abbreviated names).
CITY_ALIASES = {
    "gta": "toronto",  # treat GTA-named pages as Toronto
}


def parse_terminal_slug(slug: str) -> tuple[str, str] | None:
    """Return (service_category, city_slug) for a terminal-style slug, or None.

    city_slug may be "" for national/exact-match terminals.
    """
    if slug in EXACT_TERMINAL_SLUGS:
        return EXACT_TERMINAL_SLUGS[slug], ""
    for prefix, cat in TERMINAL_PREFIXES:
        if slug.startswith(prefix):
            city = slug[len(prefix):].strip("-")
            if not city:
                return None
            city = CITY_ALIASES.get(city, city)
            return cat, city
    return None


# Pages that are clearly not service/location: blog, info, utility.
NON_PAGE_SLUGS = {
    "blog", "book-now", "client-testimonials", "company-policy-of-amaximum-construction",
    "expert-tips", "our-work-process", "portfolio", "sitemap", "thank-you-page",
    "what-we-do", "why-choose-us", "amaximum-deck-builder-blog",
    "installation-timelines", "supply-my-own-materials",
    "handyman-charges", "handyman-drywall-repair", "handyman-furniture-assembly",
    "rate-for-a-handyman",
    "first-steps-renovation-permits", "legal-considerations-renovating",
    "material-costs-in-billing-explained", "understanding-additional-service-costs",
    "understanding-cost-building", "contractor-not-warranty",
    "contractor-warranty-client-materials-guide", "effective-communication",
    "expensive-parts-basement-renovation",
}


# ---------------------------------------------------------------------------
# 2. Section-stripping helper.
# ---------------------------------------------------------------------------


def _strip_one(html: str, open_re: re.Pattern[str]) -> tuple[str, bool]:
    m = open_re.search(html)
    if not m:
        return html, False
    section_open = re.compile(r"<section\b", re.IGNORECASE)
    section_close = re.compile(r"</section>", re.IGNORECASE)
    depth = 1
    pos = m.end()
    end_pos: int | None = None
    while pos < len(html):
        o = section_open.search(html, pos)
        c = section_close.search(html, pos)
        if c is None:
            break
        if o is not None and o.start() < c.start():
            depth += 1
            pos = o.end()
        else:
            depth -= 1
            pos = c.end()
            if depth == 0:
                end_pos = pos
                break
    if end_pos is None:
        return html, False
    return html[: m.start()] + html[end_pos:], True


def strip_block_by_id(html: str, section_id: str) -> tuple[str, bool]:
    """Remove every balanced <section ... id="<section_id>"...>...</section>."""
    pat = re.compile(
        r'<section[^>]*\bid="' + re.escape(section_id) + r'"[^>]*>',
        flags=re.IGNORECASE,
    )
    changed_any = False
    while True:
        html, c = _strip_one(html, pat)
        if not c:
            break
        changed_any = True
    return html, changed_any


def strip_block_by_class(html: str, class_token: str) -> tuple[str, bool]:
    """Remove every balanced <section ... class="... <class_token> ..." ...>...</section>."""
    pat = re.compile(
        r'<section[^>]*\bclass="[^"]*\b' + re.escape(class_token) + r'\b[^"]*"[^>]*>',
        flags=re.IGNORECASE,
    )
    changed_any = False
    while True:
        html, c = _strip_one(html, pat)
        if not c:
            break
        changed_any = True
    return html, changed_any


# ---------------------------------------------------------------------------
# 3. Build terminal index.
# ---------------------------------------------------------------------------


def build_terminal_index() -> tuple[dict[tuple[str, str], str], list[Path]]:
    """Returns ((service_cat, city_slug) -> terminal_slug, list_of_terminal_paths)."""
    index: dict[tuple[str, str], str] = {}
    terminals: list[Path] = []
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        slug = d.name
        if slug in SERVICE_HUBS:
            continue
        if slug in {"locations", "blog", "css", "js", "img", "fonts", "node_modules",
                    ".venv", ".git", "img-quality", "old-images"}:
            continue
        if slug in NON_PAGE_SLUGS:
            continue
        idx = d / "index.html"
        if not idx.exists():
            continue
        parsed = parse_terminal_slug(slug)
        if parsed is None:
            continue
        service_cat, city = parsed
        terminals.append(idx)
        if city:
            index.setdefault((service_cat, city), slug)
    return index, terminals


# ---------------------------------------------------------------------------
# 4. PASS A: strip cross-blocks from terminal pages.
# ---------------------------------------------------------------------------


def pass_a_strip_terminals(terminals: Iterable[Path]) -> int:
    changed = 0
    for path in terminals:
        text = path.read_text(encoding="utf-8")
        new, c1 = strip_block_by_id(text, "service-areas")
        new, c2 = strip_block_by_id(new, "articles")
        new, c3 = strip_block_by_class(new, "service-locations")
        new, c4 = strip_block_by_class(new, "related-articles")
        if c1 or c2 or c3 or c4:
            path.write_bytes(new.encode("utf-8"))
            changed += 1
    return changed


# ---------------------------------------------------------------------------
# 5. PASS B: redirect service hub .location-card hrefs.
# ---------------------------------------------------------------------------

LOCATION_CARD_RE = re.compile(
    r'(<a[^>]*class="location-card"[^>]*\bhref=")/locations/([a-z0-9-]+)/(")',
    flags=re.IGNORECASE,
)


def pass_b_fix_hubs(index: dict[tuple[str, str], str]) -> int:
    changed = 0
    for hub_slug, cat in SERVICE_HUBS.items():
        path = ROOT / hub_slug / "index.html"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")

        def repl(m: re.Match[str]) -> str:
            city = m.group(2)
            terminal = index.get((cat, city))
            if not terminal:
                return m.group(0)  # leave as-is; will be cleaned later
            return f"{m.group(1)}/{terminal}/{m.group(3)}"

        new = LOCATION_CARD_RE.sub(repl, text)
        if new != text:
            path.write_bytes(new.encode("utf-8"))
            changed += 1
    return changed


# ---------------------------------------------------------------------------
# 6. PASS C: redirect location hub service cards.
# ---------------------------------------------------------------------------

# Match any `<a class="card" href="/<slug>/">` (or with href first).
SERVICE_CARD_RE = re.compile(
    r'(<a\b[^>]*\bclass="card"[^>]*\bhref=")/([a-z0-9-]+)/(")',
    flags=re.IGNORECASE,
)
SERVICE_CARD_RE_ALT = re.compile(
    r'(<a\b[^>]*\bhref=")/([a-z0-9-]+)/("[^>]*\bclass="card")',
    flags=re.IGNORECASE,
)


def pass_c_fix_location_hubs(index: dict[tuple[str, str], str]) -> int:
    changed = 0
    loc_root = ROOT / "locations"
    if not loc_root.exists():
        return 0
    for city_dir in sorted(loc_root.iterdir()):
        if not city_dir.is_dir():
            continue
        path = city_dir / "index.html"
        if not path.exists():
            continue
        city_slug = city_dir.name
        text = path.read_text(encoding="utf-8")

        def make_repl(group_link_order: bool):
            def repl(m: re.Match[str]) -> str:
                href_slug = m.group(2)
                cat = SERVICE_HUBS.get(href_slug)
                if cat is None:
                    return m.group(0)  # not a known hub link, leave it
                terminal = index.get((cat, city_slug))
                if not terminal:
                    return m.group(0)  # no terminal for this combo
                return f"{m.group(1)}/{terminal}/{m.group(3)}"
            return repl

        new = SERVICE_CARD_RE.sub(make_repl(True), text)
        new = SERVICE_CARD_RE_ALT.sub(make_repl(False), new)
        if new != text:
            path.write_bytes(new.encode("utf-8"))
            changed += 1
    return changed


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------


def main() -> None:
    print("Building terminal index...")
    index, terminals = build_terminal_index()
    print(f"  Found {len(terminals)} terminal pages")
    print(f"  Unique (service, city) keys: {len(index)}")

    print("\nPASS A: stripping cross-blocks from terminal pages...")
    a = pass_a_strip_terminals(terminals)
    print(f"  Modified {a} terminal pages")

    print("\nPASS B: redirecting service-hub .location-card links...")
    b = pass_b_fix_hubs(index)
    print(f"  Modified {b} hub pages")

    print("\nPASS C: redirecting location-hub service-card links...")
    c = pass_c_fix_location_hubs(index)
    print(f"  Modified {c} location-hub pages")

    print(f"\nDone. Touched files: A={a}  B={b}  C={c}")


if __name__ == "__main__":
    main()
