# -*- coding: utf-8 -*-
"""
Standardize SEO metadata on all service hub pages.
Updates: <title>, meta description, og:title, og:description,
         <h1> (only for weak hubs), lead <p> (only for weak hubs),
         breadcrumb JSON-LD (2-level -> 3-level).
Does NOT touch: galleries, FAQ, why-choose, locations grid, suppliers,
                related articles, reviews, footer, schema other than breadcrumb.
"""
from pathlib import Path
import re

ROOT = Path(__file__).parent

# slug -> (display_name_in_breadcrumb, h1_text, lead_text_or_None_to_skip,
#         meta_description, title)
HUBS = {
    "deck-builder": dict(
        crumb="Deck Building",
        h1="Deck Building Services in Toronto & GTA",
        lead=None,  # already good
        title="Deck Building Services in Toronto & GTA | aMaximum Construction",
        desc="Custom deck building in Toronto & GTA — pressure-treated wood, composite, cedar, multi-level designs, stairs, and railings. Licensed, insured, code-aligned. Free quotes from aMaximum Construction.",
    ),
    "deck-railings": dict(
        crumb="Deck Railings",
        h1="Deck Railing Installation in Toronto & GTA",
        lead=None,
        title="Deck Railing Installation in Toronto & GTA | aMaximum Construction",
        desc="Deck railing installation in Toronto & GTA — cable, glass, aluminum, composite, and wood railing systems. Code-aligned, structurally sound. Free quotes from aMaximum Construction.",
    ),
    "fence-installation": dict(
        crumb="Fence Installation",
        h1="Fence Installation in Toronto & GTA",
        lead=None,
        title="Fence Installation in Toronto & GTA | aMaximum Construction",
        desc="Professional fence installation in Toronto & GTA — wood, vinyl, chain-link, privacy fences, gates, and post replacement. Licensed, insured, permit-aware. Free on-site quotes from aMaximum Construction.",
    ),
    "bathroom-renovation": dict(
        crumb="Bathroom Renovation",
        h1="Bathroom Renovation in Toronto & GTA",
        lead="aMaximum Construction delivers complete bathroom renovations across Toronto and the Greater Toronto Area — full remodels, tile work, vanities, plumbing, fixtures, lighting, and ventilation. Licensed, insured, and code-aligned, with clear scope and tidy execution.",
        title="Bathroom Renovation in Toronto & GTA | aMaximum Construction",
        desc="Bathroom renovation in Toronto & GTA — full remodels, tile, vanities, plumbing, fixtures, lighting, and ventilation. Licensed, insured, code-aligned. Free quotes from aMaximum Construction.",
    ),
    "basement-renovation": dict(
        crumb="Basement Renovation",
        h1="Basement Renovation in Toronto & GTA",
        lead=None,
        title="Basement Renovation in Toronto & GTA | aMaximum Construction",
        desc="Full-service basement renovation in Toronto & GTA — finishing, framing, drywall, electrical, plumbing, waterproofing, and legal second-suite conversions. Licensed, insured, permit-managed. Free quotes from aMaximum Construction.",
    ),
    "handyman-plumbing-services": dict(
        crumb="Plumbing Services",
        h1="Plumbing Services in Toronto & GTA",
        lead=None,
        title="Plumbing Services in Toronto & GTA | aMaximum Construction",
        desc="Licensed plumbing services in Toronto & GTA — leaks, faucets, toilets, drain cleaning, fixture installation, and pipe repairs. Insured, code-aligned. Free quotes from aMaximum Construction.",
    ),
    "canopy": dict(
        crumb="Canopy & Awnings",
        h1="Canopy & Awning Installation in Toronto & GTA",
        lead=None,
        title="Canopy & Awning Installation in Toronto & GTA | aMaximum Construction",
        desc="Canopy and awning installation in Toronto & GTA — retractable awnings, fixed canopies, pergolas, patio covers, and custom shade structures. Licensed, insured. Free quotes from aMaximum Construction.",
    ),
    "landscaping-services": dict(
        crumb="Landscaping Services",
        h1="Landscaping Services in Toronto & GTA",
        lead=None,
        title="Landscaping Services in Toronto & GTA | aMaximum Construction",
        desc="Professional landscaping services in Toronto & GTA — sod installation, garden design, planting, hardscape features, retaining walls, and complete yard transformations. Licensed, insured. Free on-site quotes from aMaximum Construction.",
    ),
    "general-contractor": dict(
        crumb="General Contractor",
        h1="General Contractor Services in Toronto & GTA",
        lead=None,
        title="General Contractor Services in Toronto & GTA | aMaximum Construction",
        desc="Licensed general contractor in Toronto & GTA — project management, multi-trade coordination, permits, renovations, additions, and full residential builds. Insured, permit-managed. Free quotes from aMaximum Construction.",
    ),
    "handyman-services": dict(
        crumb="Handyman Services",
        h1="Handyman Services in Toronto & GTA",
        lead=None,
        title="Handyman Services in Toronto & GTA | aMaximum Construction",
        desc="Handyman services in Toronto & GTA — drywall, painting, furniture assembly, minor plumbing & electrical, repairs and small upgrades. Licensed, insured, code-aligned. Free quotes from aMaximum Construction.",
    ),
    "interlocking-paver-services": dict(
        crumb="Interlocking & Paver Services",
        h1="Interlocking & Paver Services in Toronto & GTA",
        lead=None,
        title="Interlocking & Paver Services in Toronto & GTA | aMaximum Construction",
        desc="Interlocking and paver services in Toronto & GTA — driveways, walkways, patios, retaining walls, and pool coping. Long-term stability and intentional layout design. Free quotes from aMaximum Construction.",
    ),
    "carpenter-services": dict(
        crumb="Carpentry Services",
        h1="Carpentry Services in Toronto & GTA",
        lead=None,
        title="Carpentry Services in Toronto & GTA | aMaximum Construction",
        desc="Carpentry services in Toronto & GTA — trim, framing, custom millwork, doors, finish carpentry, and custom wood details for interior and exterior. Licensed, insured. Free quotes from aMaximum Construction.",
    ),
    "electrical-handyman-services": dict(
        crumb="Electrical Handyman Services",
        h1="Electrical Handyman Services in Toronto & GTA",
        lead=None,
        title="Electrical Handyman Services in Toronto & GTA | aMaximum Construction",
        desc="Electrical handyman services in Toronto & GTA — fixture swaps, outlet installation, ceiling fans, dimmer switches, and light upgrades. Licensed electricians. Free quotes from aMaximum Construction.",
    ),
    "handyman-painting-services": dict(
        crumb="Painting Services",
        h1="Painting Services in Toronto & GTA",
        lead=None,
        title="Painting Services in Toronto & GTA | aMaximum Construction",
        desc="Painting services in Toronto & GTA — interior and exterior painting, touch-ups, trim, doors, and finishing. Clean, even results from licensed, insured painters. Free quotes from aMaximum Construction.",
    ),
    "demolition-services": dict(
        crumb="Demolition Services",
        h1="Demolition Services in Toronto & GTA",
        lead=None,
        title="Demolition Services in Toronto & GTA | aMaximum Construction",
        desc="Demolition services in Toronto & GTA — interior demolition, kitchen and bathroom strip-out, debris removal, and site preparation for renovation. Licensed, insured. Free quotes from aMaximum Construction.",
    ),
    "excavation-services": dict(
        crumb="Excavation Services",
        h1="Excavation Services in Toronto & GTA",
        lead=None,
        title="Excavation Services in Toronto & GTA | aMaximum Construction",
        desc="Excavation services in Toronto & GTA — site grading, foundation excavation, soil removal, and trenching for landscaping and construction projects. Licensed, insured. Free quotes from aMaximum Construction.",
    ),
    "home-renovation": dict(
        crumb="Home Renovation",
        h1="Home Renovation in Toronto & GTA",
        lead=None,
        title="Home Renovation in Toronto & GTA | aMaximum Construction",
        desc="Home renovation in Toronto & GTA — kitchens, bathrooms, basements, additions, and full-property updates with coordinated trades. Licensed, insured, permit-managed. Free quotes from aMaximum Construction.",
    ),
    "christmas-lights-installation-toronto-gta": dict(
        crumb="Christmas Lights Installation",
        h1="Christmas Lights Installation in Toronto & GTA",
        lead=None,
        title="Christmas Lights Installation in Toronto & GTA | aMaximum Construction",
        desc="Christmas lights installation in Toronto & GTA — residential and commercial holiday lighting, professional install, takedown, and storage. Licensed, insured. Free quotes from aMaximum Construction.",
    ),
    "handyman-drywall-repair": dict(
        crumb="Drywall Repair Services",
        h1="Drywall Repair Services in Toronto & GTA",
        lead="aMaximum Construction provides professional drywall repair across Toronto and the Greater Toronto Area — hole patching, crack repair, water damage restoration, taping, and mudding. Licensed, insured handyman team with fast scheduling and transparent pricing.",
        title="Drywall Repair Services in Toronto & GTA | aMaximum Construction",
        desc="Drywall repair services in Toronto & GTA — hole patching, crack repair, water damage restoration, taping, and mudding. Licensed, insured handyman contractor. Free quotes from aMaximum Construction.",
    ),
    "handyman-furniture-assembly": dict(
        crumb="Furniture Assembly Services",
        h1="Furniture Assembly Services in Toronto & GTA",
        lead="aMaximum Construction provides professional furniture assembly across Toronto and the Greater Toronto Area — IKEA, Wayfair, flat-pack, beds, desks, wardrobes, and custom builds. Licensed, insured handyman team with fast scheduling and transparent pricing.",
        title="Furniture Assembly Services in Toronto & GTA | aMaximum Construction",
        desc="Furniture assembly services in Toronto & GTA — IKEA, Wayfair, flat-pack, beds, desks, wardrobes, and custom builds. Licensed, insured handyman contractor. Free quotes from aMaximum Construction.",
    ),
}


def html_escape_amp(s: str) -> str:
    """Escape & to &amp; (but leave already-escaped &amp;/&lt;/&gt;/&quot; alone)."""
    # Only replace standalone & not followed by amp;|lt;|gt;|quot;|#
    return re.sub(r'&(?!(amp|lt|gt|quot|#\d+|#x[0-9a-fA-F]+);)', '&amp;', s)


def attr_escape(s: str) -> str:
    """Escape for attribute value: & and "."""
    return html_escape_amp(s).replace('"', '&quot;')


def update_hub(slug: str, cfg: dict) -> tuple[bool, list[str]]:
    f = ROOT / slug / "index.html"
    if not f.exists():
        return False, [f"NOT FOUND: {f}"]
    text = f.read_text(encoding="utf-8")
    original = text
    notes = []

    h1_html = html_escape_amp(cfg["h1"])
    title_html = html_escape_amp(cfg["title"])
    desc_attr = attr_escape(cfg["desc"])
    crumb_html = html_escape_amp(cfg["crumb"])
    crumb_attr = attr_escape(cfg["crumb"])  # for JSON

    # ---- 1. <title> ----
    new_text, n = re.subn(
        r"<title>[^<]*</title>",
        f"<title>{title_html}</title>",
        text, count=1)
    if n: notes.append("title")
    text = new_text

    # ---- 2. meta description ----
    new_text, n = re.subn(
        r'<meta\s+name="description"\s+content="[^"]*"\s*/?>',
        f'<meta name="description" content="{desc_attr}">',
        text, count=1)
    if not n:
        new_text, n = re.subn(
            r'<meta\s+content="[^"]*"\s+name="description"\s*/?>',
            f'<meta name="description" content="{desc_attr}">',
            text, count=1)
    if n:
        notes.append("desc")
    else:
        # try inserting after <meta charset=...>
        new_text, n = re.subn(
            r'(<meta charset="[^"]+">)',
            r'\1\n  <meta name="description" content="' + desc_attr + r'">',
            text, count=1)
        if n: notes.append("desc-inserted")
    text = new_text

    # ---- 3. og:title ----
    new_text, n = re.subn(
        r'<meta\s+property="og:title"\s+content="[^"]*"\s*/?>',
        f'<meta property="og:title" content="{title_html}">',
        text, count=1)
    if not n:
        new_text, n = re.subn(
            r'<meta\s+content="[^"]*"\s+property="og:title"\s*/?>',
            f'<meta property="og:title" content="{title_html}">',
            text, count=1)
    if n: notes.append("og:title")
    text = new_text

    # ---- 4. og:description ----
    new_text, n = re.subn(
        r'<meta\s+property="og:description"\s+content="[^"]*"\s*/?>',
        f'<meta property="og:description" content="{desc_attr}">',
        text, count=1)
    if not n:
        new_text, n = re.subn(
            r'<meta\s+content="[^"]*"\s+property="og:description"\s*/?>',
            f'<meta property="og:description" content="{desc_attr}">',
            text, count=1)
    if n: notes.append("og:desc")
    text = new_text

    # ---- 5. <h1> (only the FIRST h1 in page-hero) ----
    # Match first <h1> regardless of attributes
    new_text, n = re.subn(
        r'<h1\b[^>]*>[^<]*</h1>',
        f'<h1>{h1_html}</h1>',
        text, count=1)
    if n: notes.append("h1")
    text = new_text

    # ---- 6. lead <p> right after h1 (only if cfg.lead provided) ----
    if cfg["lead"]:
        lead_html = html_escape_amp(cfg["lead"])
        new_text, n = re.subn(
            r'(<h1>[^<]+</h1>\s*)<p[^>]*>[^<]*</p>',
            r'\1<p>' + lead_html + '</p>',
            text, count=1)
        if n: notes.append("lead")
        text = new_text

    # ---- 7. breadcrumb 2-level -> 3-level ----
    # Pattern: position 2 is the hub itself (no Services intermediate)
    crumb_pattern = re.compile(
        r'(\{"@type":\s*"ListItem",\s*"position":\s*1,[^}]+\},\s*)'
        r'(\{"@type":\s*"ListItem",\s*"position":\s*2,\s*"name":\s*")'
        r'([^"]+)("\s*,\s*"item":\s*")'
        r'(https://amaximumconstruction\.com/' + re.escape(slug) + r'/?)("\s*\})'
    )
    def crumb_repl(m):
        return (
            m.group(1)
            + '{"@type": "ListItem", "position": 2, "name": "Services", '
              '"item": "https://amaximumconstruction.com/#services"},\n        '
            + '{"@type": "ListItem", "position": 3, "name": "'
            + crumb_attr
            + '", "item": "' + m.group(5) + '"}'
        )
    new_text, n = crumb_pattern.subn(crumb_repl, text, count=1)
    if n: notes.append("crumb")
    text = new_text

    if text != original:
        f.write_bytes(text.encode("utf-8"))
        return True, notes
    return False, ["no-change"]


def main():
    print(f"{'slug':<45} | {'changed':<7} | notes")
    print("-" * 110)
    for slug, cfg in HUBS.items():
        changed, notes = update_hub(slug, cfg)
        print(f"{slug:<45} | {str(changed):<7} | {', '.join(notes)}")


if __name__ == "__main__":
    main()
