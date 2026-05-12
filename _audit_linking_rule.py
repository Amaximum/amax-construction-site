"""
Audit pages against the user's rule:

  HUB pages (service without city) = should have:
    - card with "other services" (cross-service links)
    - card with "all locations of this service"

  SERVICE+LOCATION pages = should have:
    - NO "other services" card (no cross-service links besides nav)
    - card with "other locations of THIS service"

Detection heuristics:
  - "other services" block: count internal links to *different* service families
    that appear inside any element with class containing 'service' or after the
    main content (excluding header nav and footer).
  - "other locations of same service" block: count links to pages with the same
    service-family prefix but different city.
"""
from __future__ import annotations
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent

# Service families: prefix -> friendly name. Each (prefix, suffix-style) defines a family.
# We treat anything matching the prefix as "same family" regardless of city/keyword variant.
FAMILIES: list[tuple[str, str]] = [
    # (regex matching slug, family-id)
    (r"^carpenter-services-", "carpenter"),
    (r"^demolition-service(s)?(-in)?-", "demolition"),
    (r"^bathroom(s)?-renovation-(in-)?", "bathroom-renovation"),
    (r"^basement-renovation-service-in-", "basement-renovation"),
    (r"^basement(-and)?-bathroom-renovation-(in-)?", "basement-bathroom-renovation"),
    (r"^home-renovation-", "home-renovation"),
    (r"^renovation-services-in-", "renovation-services"),
    (r"^handyman-service-in-", "handyman-in"),
    (r"^handyman-services-(in-)?", "handyman-services"),
    (r"^fence-contractor-in-", "fence-contractor"),
    (r"^fence-installer-", "fence-installer"),
    (r"^general-contractor-in-", "general-contractor"),
    (r"^interlocking-stone-services-(in-)?", "interlocking-stone"),
    (r"^deck-builder-", "deck-builder"),
    (r"^deck-contractor-(in-)?", "deck-contractor"),
    (r"^deck-railing-(installer|builder|installation)(-in)?-", "deck-railing"),
    (r"^deck-railing-", "deck-railing"),
    (r"^christmas-lights-installation-in-", "christmas-installation"),
    (r"^professional-christmas-lights-installer-", "christmas-installer"),
    (r"^privacy-screen-installation-in-", "privacy-screen"),
]

HUB_SLUGS = {
    "deck-builder", "deck-railings", "fence-contractor-in-toronto",
    "general-contractor-in-toronto", "carpenter-services", "bathroom-renovation",
    "home-renovation", "demolition-services", "interlocking-paver-services",
    "interlocking-stone-services-in-toronto", "landscaping-services-toronto",
    "handyman-painting-services", "handyman-plumbing-services",
    "electrical-handyman-services", "handyman-service-in-toronto",
    "excavation-services", "canopy", "christmas-lights-installation-toronto-gta",
    "fence-installation",
}


def slug_family(slug: str) -> tuple[str, str | None]:
    """Return (family_id, city_slug) for a service+location page, or ('', None) otherwise."""
    for pattern, fam in FAMILIES:
        m = re.match(pattern, slug)
        if m:
            city = slug[m.end():]
            if city:
                return fam, city
    return "", None


def find_pages() -> list[Path]:
    out = []
    for d in ROOT.iterdir():
        if not d.is_dir():
            continue
        if d.name in {".git", "node_modules", ".venv", "__pycache__", "blog", "locations", "portfolio", "img", "css", "js"}:
            continue
        f = d / "index.html"
        if f.exists():
            out.append(f)
    return out


def extract_main_links(html: str) -> set[str]:
    """Extract internal href targets that are likely from main content
    (skip header.topbar and footer)."""
    # crude: drop everything before </header> and after <footer>
    body = html
    m = re.search(r"</header>", body)
    if m:
        body = body[m.end():]
    m = re.search(r"<footer", body)
    if m:
        body = body[:m.start()]
    hrefs = re.findall(r'href="(/[^"#?]+/?)"', body)
    return {h.rstrip("/") + "/" for h in hrefs if not h.startswith("/img") and not h.startswith("/css") and not h.startswith("/js")}


def slug_of(url: str) -> str:
    return url.strip("/").split("/")[0]


def main() -> None:
    pages = find_pages()
    # Build family -> set of city pages, to verify "other locations" links
    fam_to_pages: dict[str, set[str]] = defaultdict(set)
    page_kind: dict[str, str] = {}  # slug -> 'hub'|'svc-loc'|'other'
    for f in pages:
        slug = f.parent.name
        fam, city = slug_family(slug)
        if fam:
            fam_to_pages[fam].add(slug)
            page_kind[slug] = "svc-loc"
        elif slug in HUB_SLUGS:
            page_kind[slug] = "hub"
        else:
            page_kind[slug] = "other"

    print(f"Pages: {len(pages)}")
    print(f"Service families found: {len(fam_to_pages)}")
    for fam, slugs in sorted(fam_to_pages.items()):
        print(f"  {fam:30s} -> {len(slugs):3d} city pages")

    # Audit each service+location page.
    print("\n=== SERVICE+LOCATION pages audit ===\n")
    bad_has_other_services = []
    bad_no_sibling_locations = []
    ok = 0
    for f in pages:
        slug = f.parent.name
        if page_kind.get(slug) != "svc-loc":
            continue
        fam, city = slug_family(slug)
        siblings = fam_to_pages[fam] - {slug}
        html = f.read_text(encoding="utf-8", errors="ignore")
        links = extract_main_links(html)
        link_slugs = {slug_of(u) for u in links}

        # Cross-service links = links to other service families OR other hubs
        cross = []
        for ls in link_slugs:
            if not ls or ls == slug:
                continue
            other_fam, _ = slug_family(ls)
            if other_fam and other_fam != fam:
                cross.append(ls)
            elif ls in HUB_SLUGS:
                cross.append(ls)

        # Sibling location links (same service family, different city)
        sib_links = [ls for ls in link_slugs if ls in siblings]

        problem_other = len(cross) >= 3  # tolerate 0-2 stray links
        problem_no_sib = len(sib_links) == 0 and len(siblings) > 0

        if problem_other:
            bad_has_other_services.append((slug, len(cross), sorted(cross)[:6]))
        if problem_no_sib:
            bad_no_sibling_locations.append((slug, fam, len(siblings)))
        if not problem_other and not problem_no_sib:
            ok += 1

    print(f"OK pages: {ok}")
    print(f"\nPages with TOO MANY cross-service links ({len(bad_has_other_services)}):")
    for s, n, sample in bad_has_other_services[:30]:
        print(f"  {s:50s}  cross={n:3d}  sample={sample}")
    if len(bad_has_other_services) > 30:
        print(f"  ... and {len(bad_has_other_services)-30} more")

    print(f"\nPages with NO sibling-location links ({len(bad_no_sibling_locations)}):")
    for s, fam, sib in bad_no_sibling_locations[:30]:
        print(f"  {s:50s}  family={fam}  siblings_available={sib}")
    if len(bad_no_sibling_locations) > 30:
        print(f"  ... and {len(bad_no_sibling_locations)-30} more")

    # Audit HUB pages: they SHOULD have other-service and locations cards
    print("\n=== HUB pages audit ===\n")
    for f in pages:
        slug = f.parent.name
        if page_kind.get(slug) != "hub":
            continue
        html = f.read_text(encoding="utf-8", errors="ignore")
        links = extract_main_links(html)
        link_slugs = {slug_of(u) for u in links}
        # cross-service hub links count
        cross = [ls for ls in link_slugs if ls in HUB_SLUGS and ls != slug]
        # location children: pages that reference THIS hub's family
        # (use a simple keyword from slug as family hint)
        kw = slug.replace("-services", "").replace("-in-toronto", "").replace("services-toronto", "")
        loc_links = [ls for ls in link_slugs if kw in ls and ls != slug]
        print(f"  {slug:50s}  cross-svc={len(cross):2d}  loc-links={len(loc_links):2d}")


if __name__ == "__main__":
    main()
