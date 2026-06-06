"""Inject "Why Clients Choose This Team" + service-specific split island on every
service hub, service-in-city, and location-hub page.

Insertion point: immediately before <section ... id="trusted-suppliers" ...>
(per page-section-order rule). Idempotent: skips pages that already contain
id="why".
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Right-card variants (title + 5 bullets) per service category.
# ---------------------------------------------------------------------------

LEFT_CARD = (
    "<h3>Why Clients Choose This Team</h3>\n"
    "        <ul class=\"check\">\n"
    "          <li>Clear scope before start</li>\n"
    "          <li>Transparent communication</li>\n"
    "          <li>Respectful and tidy jobsite</li>\n"
    "          <li>Multi-trade coordination in fewer visits</li>\n"
    "          <li>Practical recommendations for long-term value</li>\n"
    "        </ul>"
)

VARIANTS: dict[str, tuple[str, list[str]]] = {
    "deck": (
        "Decks Built to Last in Every Season",
        [
            "Weather-resistant materials chosen for the GTA climate",
            "Frame, joists, and railings engineered to code",
            "Clean cuts and tight finish on every board",
            "Footings installed for long-term stability",
            "Detailed final walkthrough before payment",
        ],
    ),
    "railing": (
        "Railings Aligned, Anchored, and Code-Compliant",
        [
            "Posts mounted into sound structural framing",
            "Spindle and cable spacing checked to code",
            "Hardware rated for outdoor exposure",
            "Top rails leveled across every section",
            "Final shake-test before sign-off",
        ],
    ),
    "fence": (
        "Privacy and Property Lines Done Right",
        [
            "Survey-aware layout to respect property lines",
            "Posts set below frost line for stability",
            "Pickets, panels, and gates aligned with precision",
            "Hardware rated for long-term outdoor use",
            "Cleanup and waste removal after install",
        ],
    ),
    "bathroom": (
        "Bathrooms That Hold Up to Daily Use",
        [
            "Waterproofing completed before any tile goes up",
            "Ventilation sized to prevent moisture damage",
            "Plumbing rough-ins double-checked before close",
            "Tile lines, grout, and silicone finished cleanly",
            "Final fixtures installed and tested under load",
        ],
    ),
    "basement": (
        "Dry, Bright, and Code-Compliant Basements",
        [
            "Moisture control addressed before framing begins",
            "Egress and ceiling-height standards respected",
            "Insulation, vapor barrier, and drywall layered correctly",
            "Electrical and plumbing routed for future access",
            "Flooring and trim finished to upper-floor standard",
        ],
    ),
    "plumbing": (
        "Plumbing That Stops Costing You Later",
        [
            "Existing lines inspected before any work begins",
            "Shut-offs tested and replaced when needed",
            "Fittings and connections checked under pressure",
            "Workspace protected and cleaned after every visit",
            "Clear explanation of what was done and why",
        ],
    ),
    "canopy": (
        "Outdoor Shade Built to Stay Put",
        [
            "Anchor points engineered for wind load",
            "Frames sized for long-span coverage",
            "Fabric or panel material chosen for UV stability",
            "Clean attachment to the existing structure",
            "Drainage planned so water doesn't pool",
        ],
    ),
    "landscaping": (
        "Outdoor Spaces That Mature Well",
        [
            "Soil and drainage assessed before planting",
            "Hardscape laid on a properly compacted base",
            "Plant choices matched to GTA conditions",
            "Edges, beds, and lawn lines kept crisp",
            "Site left tidy at the end of every visit",
        ],
    ),
    "general-contractor": (
        "One Team Accountable for the Whole Project",
        [
            "Single point of contact through every stage",
            "Permits and inspections handled correctly",
            "Trades scheduled in the right sequence",
            "Daily site cleanup and material control",
            "Final punch list closed before handover",
        ],
    ),
    "handyman": (
        "Small Jobs Done Like Big Jobs",
        [
            "Honest scope agreed before any work starts",
            "Right tools and parts brought on the first visit",
            "Protective covers used inside the home",
            "Workmanship checked before leaving",
            "Clean exit — no leftover mess",
        ],
    ),
    "interlock": (
        "Pavers That Don't Shift or Sink",
        [
            "Excavation to correct depth before base",
            "Compacted base built in proper lifts",
            "Edge restraints to lock the pattern in",
            "Polymeric sand swept and set after install",
            "Slope planned for drainage away from the house",
        ],
    ),
    "carpentry": (
        "Carpentry With Tight Tolerances",
        [
            "Material acclimated before cutting",
            "Square and level checked at every step",
            "Hidden fasteners where finish matters",
            "Trim joins planned for the cleanest sightlines",
            "Touch-ups and sanding before sign-off",
        ],
    ),
    "electrical": (
        "Safe, Code-Aware Electrical Work",
        [
            "Power confirmed off before any work",
            "Connections torqued and verified",
            "Boxes, plates, and covers fitted neatly",
            "Loads tested after install",
            "Notes left for future service access",
        ],
    ),
    "painting": (
        "Paintwork That Looks Right in Every Light",
        [
            "Surface prep, sanding, and cleaning first",
            "Trim and edges protected before paint",
            "Coats applied with proper dry time between",
            "Cut-ins kept sharp at corners and ceilings",
            "Walk-through done in daylight before sign-off",
        ],
    ),
    "demolition": (
        "Demolition Done Without Surprises",
        [
            "Utilities checked and isolated first",
            "Surrounding finishes protected before strike",
            "Debris sorted for proper disposal",
            "Dust control kept active throughout",
            "Site swept ready for the next trade",
        ],
    ),
    "excavation": (
        "Excavation That Sets Up the Next Trade",
        [
            "Utility locates done before digging",
            "Cuts kept to surveyed depth and grade",
            "Spoil handled or removed as planned",
            "Walls and edges shaped for footings",
            "Site left ready for footings or base prep",
        ],
    ),
    "home-renovation": (
        "Whole-Home Updates Without the Chaos",
        [
            "Living areas protected and isolated from work zones",
            "Daily dust control and material staging",
            "Trades coordinated so no day is wasted",
            "Selections confirmed before order and install",
            "Final detail pass before keys are returned",
        ],
    ),
    "christmas": (
        "Holiday Lighting Installed and Removed Clean",
        [
            "Roof and gutters protected by proper clips only",
            "Lines run for symmetry from the curb",
            "Bulbs and strands tested before climb-down",
            "Timers set up for the customer",
            "Full takedown and storage offered after the season",
        ],
    ),
    # Used for /locations/<city>/ hub pages.
    "location-hub": (
        "Why Local Homeowners Choose Us",
        [
            "Familiar with local permits and inspection processes",
            "Local material runs keep schedules tight",
            "References available from completed projects nearby",
            "Crew arrives prepared for site conditions",
            "Follow-up support after the project is closed",
        ],
    ),
    # Generic fallback (matches the homepage right-card content).
    "generic": (
        "Why Homeowners Trust Our Process",
        [
            "Clear communication from start to finish",
            "Organized and efficient workflow",
            "Clean and respectful work areas",
            "Fast response and reliable scheduling",
            "Long-term quality-focused solutions",
        ],
    ),
}


def build_island(category: str) -> str:
    title, bullets = VARIANTS[category]
    bullet_html = "\n".join(f"          <li>{b}</li>" for b in bullets)
    return (
        "    <section class=\"island split reveal\" id=\"why\" aria-label=\"Advantages\">\n"
        "      <span class=\"shine\" aria-hidden=\"true\"></span>\n"
        "      <article class=\"mini\">\n"
        f"        {LEFT_CARD}\n"
        "      </article>\n\n"
        "      <article class=\"mini\">\n"
        f"        <h3>{title}</h3>\n"
        "        <ul class=\"check\">\n"
        f"{bullet_html}\n"
        "        </ul>\n"
        "      </article>\n"
        "    </section>\n\n"
    )


# ---------------------------------------------------------------------------
# Slug -> category classification.
# ---------------------------------------------------------------------------

# Order matters: more specific patterns first.
PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"christmas[-_]?lights?|christmas-lights"), "christmas"),
    (re.compile(r"deck-railing|railings?"), "railing"),
    (re.compile(r"deck(?:-builder|-contractor|s)?"), "deck"),
    (re.compile(r"fence"), "fence"),
    (re.compile(r"bathroom"), "bathroom"),
    (re.compile(r"basement"), "basement"),
    (re.compile(r"plumb"), "plumbing"),
    (re.compile(r"canopy|awning"), "canopy"),
    (re.compile(r"landscap"), "landscaping"),
    (re.compile(r"general[-_ ]contractor|gc-services"), "general-contractor"),
    (re.compile(r"handyman"), "handyman"),
    (re.compile(r"interlock|paver|paving|paving-company"), "interlock"),
    (re.compile(r"carpenter|carpentry"), "carpentry"),
    (re.compile(r"electric"), "electrical"),
    (re.compile(r"paint"), "painting"),
    (re.compile(r"demolition|demo"), "demolition"),
    (re.compile(r"excavation|excavat"), "excavation"),
    (re.compile(r"home-renovation|renovation-service"), "home-renovation"),
]


def classify(rel_path: str) -> str | None:
    """Return category name for a given relative path, or None to skip."""
    p = rel_path.replace("\\", "/")

    # Location hub: /locations/<city>/index.html
    if p.startswith("locations/") and p.count("/") == 2 and p.endswith("/index.html"):
        return "location-hub"

    # The locations index itself uses the generic homepage card.
    if p == "locations/index.html":
        return "generic"

    # Single-segment slugs only (top-level service pages).
    if p.count("/") != 1 or not p.endswith("/index.html"):
        return None

    slug = p.split("/", 1)[0]

    # Hard-coded skip list: clearly non-service, non-location pages.
    SKIP_SLUGS = {
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
    if slug in SKIP_SLUGS:
        return None

    # Heuristic: blog-style article slugs tend to contain prose words. We use a
    # conservative whitelist via the PATTERNS table — anything that doesn't
    # match a recognized service keyword is treated as a blog/info page and
    # skipped.
    for pat, cat in PATTERNS:
        if pat.search(slug):
            # Extra filter: blog articles often start with words like "how-to",
            # "best-", "top-", "is-it", "what-is", "why-", "find-", "guide",
            # "tips-", "navigating-", "exploring-", "choosing-", "selecting-",
            # "expert-", "reasons-", "ultimate-", "trex-", "scammer-", "avoid",
            # "advantages-", "benefits-", "essential-", "richmond-hill-custom",
            # "search", "5-types", "3-easy", "1-basement", "a-look", "a-review".
            BLOG_PREFIXES = (
                "how-", "best-", "top-", "is-it", "what-", "why-",
                "find-", "guide-", "tips-", "navigating-", "exploring-",
                "choosing-", "choose-", "selecting-", "expert-", "reasons-",
                "ultimate-", "trex-", "scammer-", "avoid", "advantages-",
                "benefits-", "essential-", "5-", "3-", "1-", "a-",
                "accessorizing-", "affordable-", "amazing-", "backyard-",
                "blog-", "bright-", "building-", "construction-project",
                "custom-decks-richmond", "deck-maintenance", "elegant-",
                "electing-", "expert-deck", "expert-demolition",
                "expert-insights", "expert-richmond", "interior-bathroom",
                "is-it-", "small-contractors", "starting-deck",
                "torontos-top", "toronto-deck-builders",
                "trusted-small-contractors", "wood-deck-repair",
                "your-guide", "richmond-hill-custom",
                "professional-demolition", "professional-christmas-lights",
                "general-contractor-services-2",
                "renovation-services-in-toronto-2",
            )
            for pref in BLOG_PREFIXES:
                if slug.startswith(pref):
                    return None
            return cat
    return None


# ---------------------------------------------------------------------------
# HTML edit.
# ---------------------------------------------------------------------------

SUPPLIERS_RE = re.compile(
    r"(\s*)<section[^>]*\bid=\"trusted-suppliers\"[^>]*>",
    flags=re.IGNORECASE,
)

WHY_PRESENT_RE = re.compile(r"id=\"why\"", flags=re.IGNORECASE)


def inject_into(path: Path, category: str) -> str:
    text = path.read_text(encoding="utf-8")
    if WHY_PRESENT_RE.search(text):
        return "skip-existing"

    match = SUPPLIERS_RE.search(text)
    if not match:
        return "skip-no-suppliers"

    island = build_island(category)
    insert_at = match.start()
    # Preserve a clean newline before the new section.
    new_text = text[:insert_at] + "\n" + island + text[insert_at:].lstrip("\n")
    path.write_bytes(new_text.encode("utf-8"))
    return "ok"


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------


def main() -> None:
    counts: dict[str, int] = {}
    categorized: dict[str, list[str]] = {}
    for path in ROOT.rglob("index.html"):
        rel = path.relative_to(ROOT).as_posix()
        # Skip top-level homepage and anything inside dot folders / node_modules.
        if rel == "index.html":
            continue
        if any(part.startswith(".") for part in path.relative_to(ROOT).parts):
            continue

        category = classify(rel)
        if category is None:
            continue

        result = inject_into(path, category)
        key = f"{category}:{result}"
        counts[key] = counts.get(key, 0) + 1
        categorized.setdefault(category, []).append(rel)

    print("=== Per-category results ===")
    for k in sorted(counts):
        print(f"  {k:40s} {counts[k]}")
    print()
    print("=== Pages classified per category ===")
    for cat in sorted(categorized):
        print(f"  {cat:20s} {len(categorized[cat])}")


if __name__ == "__main__":
    main()
