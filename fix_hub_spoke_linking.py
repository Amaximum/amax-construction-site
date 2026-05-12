"""
Fix the 6 spokes missing hub link, 8 spokes missing sibling card, and 5 hubs
missing full city list — by injecting (or repairing) the standardized
`service-locations` section.

Idempotent: matches by id="other-locations" and rebuilds it if present;
otherwise inserts before <footer> (or before closing of last main container).

Visible content is NOT rewritten; only the navigation card is added/updated.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).parent

# Same family map as audit.
FAMILY_PATTERNS: list[tuple[str, str | None, list[str], str, str]] = [
    # (family-id, hub-slug, prefixes, friendly-service-name, hub-link-label)
    ("carpenter",         "carpenter-services",                          [r"^carpenter-services-"], "Carpentry",                "View all carpentry services"),
    ("demolition",        "demolition-services",                         [r"^demolition-service(s)?(-in)?-"], "Demolition",     "View all demolition services"),
    ("bathroom",          "bathroom-renovation",                         [r"^bathroom(s)?-renovation-(in-)?", r"^basement-(and-)?bathroom-renovation-(in-)?"], "Bathroom Renovation", "View all bathroom renovation services"),
    ("basement",          "basement-renovation-service-in-toronto",      [r"^basement-renovation-service-in-(?!toronto)", r"^best-basement-renovation-service-(in-)?(?!toronto)"], "Basement Renovation", "View all basement renovation services"),
    ("home-renovation",   "home-renovation",                             [r"^home-renovation-(?!toronto)", r"^renovation-services-in-(?!toronto)"], "Home Renovation", "View all home renovation services"),
    ("handyman",          "handyman-service-in-toronto",                 [r"^handyman-service-in-(?!toronto)", r"^handyman-services-(in-)?(?!toronto)"], "Handyman Services", "View all handyman services"),
    ("fence",             "fence-contractor-in-toronto",                 [r"^fence-contractor-in-(?!toronto)", r"^fence-installer-"], "Fence Installation", "View all fence services"),
    ("general-contractor","general-contractor-in-toronto",               [r"^general-contractor-in-(?!toronto)"], "General Contracting", "View all general contracting services"),
    ("interlocking",      "interlocking-stone-services-in-toronto",      [r"^interlocking-stone-services-(in-)?(?!toronto)"], "Interlocking Stone", "View all interlocking services"),
    ("deck-builder",      "deck-builder",                                [r"^deck-builder-(?!gta)", r"^deck-contractor-(in-)?"], "Deck Building", "View all deck builder services"),
    ("deck-railing",      "deck-railings",                               [r"^deck-railing-(installer|builder|installation)(-in)?-"], "Deck Railings", "View all deck railing services"),
    ("christmas",         "christmas-lights-installation-toronto-gta",   [r"^christmas-lights-installation-in-", r"^professional-christmas-lights-installer-"], "Christmas Lights Installation", "View all Christmas lights services"),
]


def find_pages() -> dict[str, Path]:
    out: dict[str, Path] = {}
    for d in ROOT.iterdir():
        if not d.is_dir():
            continue
        if d.name in {".git", "node_modules", ".venv", "__pycache__", "blog", "locations", "portfolio", "img", "css", "js", "img-archive"}:
            continue
        f = d / "index.html"
        if f.exists():
            out[d.name] = f
    return out


def assign(slug: str):
    for fam, hub, patterns, label, link_label in FAMILY_PATTERNS:
        if hub and slug == hub:
            return fam, True, label, link_label, hub
        for pat in patterns:
            if re.match(pat, slug):
                return fam, False, label, link_label, hub
    return None


def city_from_slug(slug: str, fam: str) -> str:
    """Pretty-print city name from a spoke slug (best-effort)."""
    for fam_id, hub, patterns, *_ in FAMILY_PATTERNS:
        if fam_id != fam:
            continue
        for pat in patterns:
            m = re.match(pat, slug)
            if m:
                rest = slug[m.end():]
                # Strip leading 'in-' if present.
                rest = re.sub(r"^in-", "", rest)
                return rest.replace("-", " ").title()
    return slug.replace("-", " ").title()


SECTION_RE = re.compile(
    r"\s*<section[^>]*id=\"other-locations\"[^>]*>.*?</section>\s*",
    re.DOTALL | re.IGNORECASE,
)
FOOTER_RE = re.compile(r"\s*<footer\b", re.IGNORECASE)
END_BODY_RE = re.compile(r"</body>", re.IGNORECASE)


def build_section(active_city: str | None, label: str, hub_slug: str | None,
                  link_label: str, siblings: list[tuple[str, str]],
                  is_hub: bool) -> str:
    """Build the standardized service-locations card.

    siblings: list of (slug, city-name).
    For hubs, active_city is None and ALL cities are linked.
    For spokes, active_city is the current city, shown as inactive label.
    """
    head_intro = "We also provide " + label.lower() + " services in these areas."
    if hub_slug:
        head_intro += f' <a href="/{hub_slug}/">{link_label} &rarr;</a>'
    cards: list[str] = []
    if active_city:
        cards.append(f'    <span class="location-card location-card-active">{active_city}</span>')
    for slug, city in sorted(siblings, key=lambda x: x[1].lower()):
        cards.append(f'    <a href="/{slug}/" class="location-card">{city}</a>')
    cards_html = "\n".join(cards)
    h2 = f"{label} in Other Areas" if not is_hub else f"{label} — Service Areas"
    return (
        '\n\n<section class="island reveal service-locations" id="other-locations" aria-label="Other locations">\n'
        '  <span class="shine" aria-hidden="true"></span>\n'
        '  <div class="section-head">\n'
        f'    <h2>{h2}</h2>\n'
        f'    <p>{head_intro}</p>\n'
        '  </div>\n'
        '  <div class="location-grid">\n'
        f'{cards_html}\n'
        '  </div>\n'
        '</section>\n'
    )


def upsert_section(html: str, section: str) -> str:
    """Replace existing #other-locations section if present, else insert before <footer>."""
    if SECTION_RE.search(html):
        return SECTION_RE.sub(section, html, count=1)
    # insert before footer
    m = FOOTER_RE.search(html)
    if m:
        return html[: m.start()] + section + html[m.start():]
    # fallback: before </body>
    m = END_BODY_RE.search(html)
    if m:
        return html[: m.start()] + section + html[m.start():]
    return html + section


def main() -> None:
    pages = find_pages()
    # Build family -> [city slugs]
    fam_cities: dict[str, list[str]] = {fam: [] for fam, *_ in FAMILY_PATTERNS}
    for slug in pages:
        info = assign(slug)
        if info and not info[1]:
            fam_cities[info[0]].append(slug)

    changed = 0
    for slug, f in pages.items():
        info = assign(slug)
        if not info:
            continue
        fam, is_hub, label, link_label, hub_slug = info
        cities = sorted(set(fam_cities[fam]) - {slug})
        siblings = [(c, city_from_slug(c, fam)) for c in cities]

        if not siblings and is_hub:
            continue  # hub with no city pages — skip
        if not siblings and not is_hub:
            continue  # standalone spoke without family siblings — skip

        active = None if is_hub else city_from_slug(slug, fam)
        section = build_section(active, label, None if is_hub else hub_slug,
                                link_label, siblings, is_hub)

        html = f.read_text(encoding="utf-8", errors="ignore")
        new_html = upsert_section(html, section)
        if new_html != html:
            f.write_bytes(new_html.encode("utf-8"))
            changed += 1
            print(f"  fixed: {slug}")

    print(f"\nTotal updated pages: {changed}")


if __name__ == "__main__":
    main()
