"""
Strict audit + fix planning per the user's hub-and-spoke rule.

For EVERY service+location page, two things MUST exist in main content:
  (A) a link to its HUB (canonical hub URL of the same service)
  (B) a card listing siblings (same service, other cities)

For EVERY HUB, the card listing all its city pages must exist.

This script ONLY reports — does not modify files.
"""
from __future__ import annotations
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent

# Explicit mapping: family-id -> (hub-slug, [city-page-slugs])
# A "service" here corresponds to one Google-targeted offering, possibly
# expressed under more than one URL keyword (deck-builder + deck-contractor
# are SAME service; bathroom-renovation + bathrooms-renovation SAME; etc.)
FAMILY_PATTERNS: list[tuple[str, str, list[str]]] = [
    # (family-id, hub-slug, list-of-prefixes-for-spoke-slugs)
    ("carpenter",        "carpenter-services",                          [r"^carpenter-services-"]),
    ("demolition",       "demolition-services",                         [r"^demolition-service(s)?(-in)?-"]),
    ("bathroom",         "bathroom-renovation",                         [r"^bathroom(s)?-renovation-(in-)?", r"^basement-(and-)?bathroom-renovation-(in-)?"]),
    ("basement",         "basement-renovation-service-in-toronto",      [r"^basement-renovation-service-in-(?!toronto)", r"^best-basement-renovation-service-(in-)?(?!toronto)"]),
    ("home-renovation",  "home-renovation",                             [r"^home-renovation-(?!toronto)", r"^renovation-services-in-(?!toronto)"]),
    ("handyman",         "handyman-service-in-toronto",                 [r"^handyman-service-in-(?!toronto)", r"^handyman-services-(in-)?(?!toronto)"]),
    ("fence",            "fence-contractor-in-toronto",                 [r"^fence-contractor-in-(?!toronto)", r"^fence-installer-"]),
    ("general-contractor","general-contractor-in-toronto",              [r"^general-contractor-in-(?!toronto)"]),
    ("interlocking",     "interlocking-stone-services-in-toronto",      [r"^interlocking-stone-services-(in-)?(?!toronto)"]),
    ("deck-builder",     "deck-builder",                                [r"^deck-builder-(?!gta)", r"^deck-contractor-(in-)?"]),
    ("deck-railing",     "deck-railings",                               [r"^deck-railing-(installer|builder|installation)(-in)?-", r"^deck-railing-(?!s$|s-toronto)"]),
    ("christmas",        "christmas-lights-installation-toronto-gta",   [r"^christmas-lights-installation-in-", r"^professional-christmas-lights-installer-"]),
    ("privacy-screen",   None,                                          [r"^privacy-screen-installation-in-"]),  # no hub yet
    # Hub-only services (no city pages currently):
    ("canopy",                  "canopy", []),
    ("excavation",              "excavation-services", []),
    ("painting",                "handyman-painting-services", []),
    ("plumbing",                "handyman-plumbing-services", []),
    ("electrical",              "electrical-handyman-services", []),
    ("landscaping",             "landscaping-services-toronto", []),
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


def assign_family(slug: str) -> tuple[str, bool] | None:
    """Return (family-id, is_hub). is_hub=True if slug is the hub slug."""
    for fam, hub, patterns in FAMILY_PATTERNS:
        if hub and slug == hub:
            return fam, True
        for pat in patterns:
            if re.match(pat, slug):
                return fam, False
    return None


def main_content_links(html: str) -> set[str]:
    body = html
    m = re.search(r"</header>", body)
    if m:
        body = body[m.end():]
    m = re.search(r"<footer", body)
    if m:
        body = body[:m.start()]
    hrefs = re.findall(r'href="(/[^"#?]+/?)"', body)
    return {h.rstrip("/") + "/" for h in hrefs}


def main() -> None:
    pages = find_pages()

    # Build family -> {hub_slug, [city_slugs]} from disk
    fam_data: dict[str, dict] = {fam: {"hub": hub, "cities": []} for fam, hub, _ in FAMILY_PATTERNS}
    for slug in pages:
        res = assign_family(slug)
        if not res:
            continue
        fam, is_hub = res
        if not is_hub:
            fam_data[fam]["cities"].append(slug)

    print("=== Service families ===")
    for fam, data in fam_data.items():
        hub_exists = data["hub"] in pages if data["hub"] else False
        print(f"  {fam:18s}  hub={data['hub'] or '-':45s}  hub_exists={hub_exists}  cities={len(data['cities'])}")

    # === Spoke audit ===
    missing_hub_link = []
    missing_sibling_card = []
    for slug, f in pages.items():
        res = assign_family(slug)
        if not res:
            continue
        fam, is_hub = res
        if is_hub:
            continue
        hub = fam_data[fam]["hub"]
        cities = [c for c in fam_data[fam]["cities"] if c != slug]
        html = f.read_text(encoding="utf-8", errors="ignore")
        links = main_content_links(html)
        link_slugs = {u.strip("/").split("/")[0] for u in links}

        if hub and hub not in link_slugs and hub in pages:
            missing_hub_link.append((slug, fam, hub))

        sib_present = sum(1 for c in cities if c in link_slugs)
        if cities and sib_present < min(3, len(cities)):
            missing_sibling_card.append((slug, fam, sib_present, len(cities)))

    print(f"\n=== SPOKES missing HUB link: {len(missing_hub_link)} ===")
    for s, fam, hub in missing_hub_link[:80]:
        print(f"  {s:50s}  fam={fam:18s}  needs->{hub}")
    if len(missing_hub_link) > 80:
        print(f"  ... and {len(missing_hub_link)-80} more")

    print(f"\n=== SPOKES missing sibling card (>=3 sib links): {len(missing_sibling_card)} ===")
    for s, fam, n, total in missing_sibling_card[:80]:
        print(f"  {s:50s}  fam={fam:18s}  has={n}/{total}")
    if len(missing_sibling_card) > 80:
        print(f"  ... and {len(missing_sibling_card)-80} more")

    # === Hub audit ===
    print("\n=== HUBS missing 'all locations' card ===")
    for fam, data in fam_data.items():
        hub = data["hub"]
        if not hub or hub not in pages:
            continue
        cities = data["cities"]
        if not cities:
            continue
        html = pages[hub].read_text(encoding="utf-8", errors="ignore")
        links = main_content_links(html)
        link_slugs = {u.strip("/").split("/")[0] for u in links}
        present = sum(1 for c in cities if c in link_slugs)
        if present < len(cities):
            print(f"  HUB {hub:45s} fam={fam:18s} has {present}/{len(cities)} city links")


if __name__ == "__main__":
    main()
