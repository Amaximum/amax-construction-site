#!/usr/bin/env python3
"""
Update 15 handyman location (spoke) pages with unique, locality-specific
content while preserving:
  * existing site structure / section order
  * every existing internal <a href> (anchor text + position)
  * existing booking endpoints
  * existing JSON-LD structure (only refreshes FAQ text & meta strings)

Reference pages (NOT modified):
  - handyman-service-in-richmond-hill/
  - handyman-service-in-north-york/
  - handyman-services/

Idempotency:
  Replacements key off the CURRENT exact template text. After a successful
  pass those source strings no longer exist, so re-running is a no-op.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent

# ---------------------------------------------------------------------------
# Per-city content. Each entry carries ONLY the unique-to-location words.
# Generators below assemble final HTML blocks from these primitives, so
# every city gets distinct prose without manual full-page authoring.
# ---------------------------------------------------------------------------

CITIES = [
    # ---------------- Category A (8) ----------------
    {
        "slug": "handyman-service-in-east-york",
        "category": "A",
        "city": "East York",
        "h1": "Handyman Service in East York",
        "gc_href": "/general-contractor-in-east-york/",
        "neighbors_short": "Leaside, Danforth, Pape Village, Broadview, and central Toronto",
        "neighbors_faq": "Leaside, Danforth, Pape Village, Riverdale, and Broadview",
        "housing": "post-war bungalows, semi-detached homes, and 1.5-storey houses",
        "local_pain": "settled foundations, original plaster walls, single-pane windows on older brick exteriors, and aged door hardware that drifts with seasonal humidity",
        "weather_note": "lake-effect humidity in summer and freeze-thaw cycles in winter that loosen caulking and warp wood trim",
        "hero_sub": "Drywall, doors, plumbing fixtures, mounting, painting — done right the first time across East York.",
        "meta_desc": "Reliable handyman service in East York for repairs, drywall, door & window fixes, faucet swaps, TV mounting and painting touch-ups. Licensed, insured, free quotes.",
        "title": "Handyman Service in East York | aMaximum Construction",
    },
    {
        "slug": "handyman-service-in-aurora",
        "category": "A",
        "city": "Aurora",
        "h1": "Handyman Service in Aurora",
        "gc_href": "/general-contractor-in-aurora/",
        "neighbors_short": "Aurora Highlands, Bayview Hill, Hills of St. Andrew, Aurora Estates, and Newmarket",
        "neighbors_faq": "Aurora Highlands, Hills of St. Andrew, Bayview Hill, Aurora Estates, and the Newmarket border",
        "housing": "executive detached homes, modern subdivisions, and heritage Yonge Street properties",
        "local_pain": "exterior caulking that fails after Aurora winters, fence posts heaved by frost, deck boards that warp on south-facing yards, and oversized double doors that drop out of alignment",
        "weather_note": "long winters with deep freeze-thaw cycles that crack caulking, lift fence posts, and stress exterior trim",
        "hero_sub": "Same-week handyman visits across Aurora — repairs, installations, weather-proofing, and finishing touches.",
        "meta_desc": "Handyman service in Aurora — drywall, door alignment, fence post repair, fixture mounting, deck board replacement, painting. Licensed, insured, written estimates.",
        "title": "Handyman Service in Aurora | aMaximum Construction",
    },
    {
        "slug": "handyman-service-in-newmarket",
        "category": "A",
        "city": "Newmarket",
        "h1": "Handyman Service in Newmarket",
        "gc_href": "/general-contractor-in-newmarket/",
        "neighbors_short": "Stonehaven, Summerhill Estates, Glenway, Woodland Hill, and Aurora",
        "neighbors_faq": "Stonehaven, Summerhill Estates, Glenway, Woodland Hill, and Bristol-London",
        "housing": "newer subdivisions, townhomes, and freehold detached homes built since the 1990s",
        "local_pain": "garage doors that need spring tune-ups, weatherstripping that cracks from cold snaps, builder-grade fixtures that wear out around the 10-year mark, and exterior caulking around bay windows",
        "weather_note": "open winter winds that drive cold air through gaps in trim, exterior outlets, and attic hatches",
        "hero_sub": "Reliable handyman visits across Newmarket — fast booking, transparent pricing, clean finish.",
        "meta_desc": "Newmarket handyman service for drywall, door & window repair, fixture installation, TV mounting, deck and fence touch-ups. Licensed, insured, same-week scheduling.",
        "title": "Handyman Service in Newmarket | aMaximum Construction",
    },
    {
        "slug": "handyman-service-in-scarborough",
        "category": "A",
        "city": "Scarborough",
        "h1": "Handyman Service in Scarborough",
        "gc_href": "/general-contractor-in-scarborough/",
        "neighbors_short": "Agincourt, Bendale, Malvern, West Hill, and Cliffside",
        "neighbors_faq": "Agincourt, Bendale, Malvern, West Hill, and the Cliffside / Birchcliff area",
        "housing": "split-level homes, side-splits, 1960s–80s detached houses, condo towers and townhome complexes",
        "local_pain": "tired aluminum windows, settling concrete around walkouts, garage side-doors that won't latch, popcorn ceilings that need patching, and brick-clad exteriors that need caulking refresh",
        "weather_note": "exposed east-end wind off the bluffs and lake that punishes weatherstripping and exterior fixtures",
        "hero_sub": "Trusted handyman team for Scarborough houses, condos, and rental units — repairs done cleanly and on schedule.",
        "meta_desc": "Scarborough handyman service: drywall, door & window repair, faucet & toilet swaps, TV mounting, deck boards, fence repair, painting. Licensed, insured, free quotes.",
        "title": "Handyman Service in Scarborough | aMaximum Construction",
    },
    {
        "slug": "handyman-service-in-etobicoke",
        "category": "A",
        "city": "Etobicoke",
        "h1": "Handyman Service in Etobicoke",
        "gc_href": "/general-contractor-in-etobicoke/",
        "neighbors_short": "Mimico, Alderwood, The Kingsway, Humber Bay, and Long Branch",
        "neighbors_faq": "Mimico, Alderwood, The Kingsway, Humber Bay Shores, and Long Branch",
        "housing": "lakeside condo towers, post-war bungalows, custom rebuilds, and 1960s ranch homes",
        "local_pain": "salt-air corrosion on exterior hardware in Mimico and Humber Bay, settling foundations on older Alderwood streets, lakefront-condo concierge-restricted move-in windows, and constant TV / mount installs in new builds",
        "weather_note": "lake-driven moisture, wind, and salt spray near the waterfront that wears down exterior caulking and metal fittings",
        "hero_sub": "Fast, clean handyman visits across Etobicoke — houses, condos, and rental units handled with care.",
        "meta_desc": "Etobicoke handyman service for drywall repair, door & window fixes, fixture install, TV mounting, deck and fence touch-ups. Licensed, insured, condo-friendly scheduling.",
        "title": "Handyman Service in Etobicoke | aMaximum Construction",
    },
    {
        "slug": "handyman-service-in-markham",
        "category": "A",
        "city": "Markham",
        "h1": "Handyman Service in Markham",
        "gc_href": "/general-contractor-in-markham/",
        "neighbors_short": "Unionville, Cornell, Berczy Village, Cathedraltown, and Wismer",
        "neighbors_faq": "Unionville, Cornell, Berczy Village, Cathedraltown, and Wismer",
        "housing": "modern detached homes, executive estates, town-home enclaves, and heritage Main Street Unionville properties",
        "local_pain": "double-height entry doors that drift, builder-grade caulking that fails by year five, fence panels heaved by frost, and constant requests for TV / smart-home mount installations",
        "weather_note": "wide temperature swings and heavy snow loads that stress fences, decks, and exterior trim",
        "hero_sub": "Trusted handyman service across Markham — repairs, installations, and finishing work done cleanly.",
        "meta_desc": "Markham handyman service: drywall, doors, fixture installation, TV mounting, deck and fence repair, painting touch-ups. Licensed, insured, written estimates.",
        "title": "Handyman Service in Markham | aMaximum Construction",
    },
    {
        "slug": "handyman-service-in-vaughan",
        "category": "A",
        "city": "Vaughan",
        "h1": "Handyman Service in Vaughan",
        "gc_href": "/general-contractor-in-vaughan/",
        "neighbors_short": "Woodbridge, Maple, Kleinburg, Thornhill, and Concord",
        "neighbors_faq": "Woodbridge, Maple, Kleinburg, Thornhill, and Patterson",
        "housing": "estate detached homes, townhouses, and newer subdivisions across Vellore, Patterson, and Kleinburg",
        "local_pain": "tall double doors that need re-shimming, exterior caulking on stone and stucco facades, fence posts heaved by Vaughan winters, and large basement-room TV / shelving installs",
        "weather_note": "cold, snowy winters that lift fence posts, crack exterior caulking, and warp deck boards",
        "hero_sub": "Reliable handyman work for Vaughan estates, family homes, and rental properties — clean, prompt, insured.",
        "meta_desc": "Vaughan handyman service: drywall repair, door alignment, fixture install, TV mounting, deck and fence touch-ups, painting. Licensed, insured, same-week visits.",
        "title": "Handyman Service in Vaughan | aMaximum Construction",
    },
    {
        "slug": "handyman-service-in-woodbridge",
        "category": "A",
        "city": "Woodbridge",
        "h1": "Handyman Service in Woodbridge",
        "gc_href": "/general-contractor-in-woodbridge/",
        "neighbors_short": "West Woodbridge, Sonoma Heights, Vellore Village, Kleinburg, and central Vaughan",
        "neighbors_faq": "West Woodbridge, Sonoma Heights, Vellore Village, Kleinburg, and Patterson",
        "housing": "executive detached homes, stone-and-brick estates, and 1990s–2010s subdivisions",
        "local_pain": "oversized front doors that drop with seasonal shift, stone-veneer caulking that needs annual review, fence posts shifted by frost, and constant interior touch-ups in higher-traffic estate homes",
        "weather_note": "cold, snow-heavy winters that lift fence posts and crack exterior caulking around stone and stucco trim",
        "hero_sub": "Professional handyman care for Woodbridge estates and family homes — quick scheduling, clean execution.",
        "meta_desc": "Woodbridge handyman service: drywall, door & window repair, fixture install, TV mounting, deck and fence repair, painting touch-ups. Licensed, insured, written estimates.",
        "title": "Handyman Service in Woodbridge | aMaximum Construction",
    },

    # ---------------- Category C (1) ----------------
    {
        "slug": "handyman-service-in-toronto",
        "category": "C",
        "city": "Toronto",
        "h1": "Handyman Services in Toronto &amp; GTA",
        "neighbors_short": "downtown, midtown, the Annex, east-end, and west-end Toronto",
        "neighbors_faq": "Downtown, Midtown, The Annex, East End, West End, and the broader GTA",
        "housing": "downtown condos, century homes, semi-detached houses, and post-war Toronto bungalows",
        "local_pain": "plaster walls in older homes, condo move-in windows with concierge restrictions, drafty original windows, and constant TV / mount and IKEA assembly requests",
        "weather_note": "Toronto's humid summers and freeze-thaw winters that work caulking, weatherstripping, and door alignment loose",
        "hero_sub": "Reliable handyman service across Toronto and the GTA — repairs, installations, and finishing work done cleanly.",
        "meta_desc": "Toronto handyman service: drywall repair, door & window fixes, fixture installation, TV mounting, furniture assembly, painting touch-ups. Licensed, insured, GTA-wide.",
        "title": "Handyman Services in Toronto & GTA | aMaximum Construction",
    },

    # ---------------- Category B (6) ----------------
    {
        "slug": "handyman-services-king-creek",
        "category": "B",
        "city": "King Creek",
        "h1": "Handyman Services in King Creek",
        "neighbors_short": "King City, Nobleton, Kettleby, Snowball, and the broader King Township",
        "neighbors_faq": "King City, Nobleton, Kettleby, Snowball, and the rest of King Township",
        "housing": "estate homes on large lots, century farmhouses, and custom rural builds",
        "local_pain": "long driveway gate hardware, exterior carpentry exposed to wind and snow, mudroom doors with heavy use, well-pump fixtures and rural plumbing tie-ins, and detached garage / barn touch-ups",
        "weather_note": "open rural exposure with deeper snow loads and stronger wind than central GTA, which punishes fences, fascia and exterior caulking",
        "hero_sub": "Quiet, reliable handyman visits for King Creek estate homes and country properties.",
        "meta_desc": "King Creek handyman: drywall, door & window repair, fixture install, painting touch-ups, deck and fence repair on estate and rural properties. Licensed, insured.",
        "title": "Handyman Services in King Creek | aMaximum Construction",
    },
    {
        "slug": "handyman-services-bayview-glen",
        "category": "B",
        "city": "Bayview Glen",
        "h1": "Handyman Services in Bayview Glen",
        "neighbors_short": "Thornhill, Royal Orchard, German Mills, Langstaff, and Bayview Village",
        "neighbors_faq": "Thornhill, Royal Orchard, German Mills, Langstaff, and Bayview Village",
        "housing": "luxury estate homes on mature treed lots, custom rebuilds, and well-appointed family properties",
        "local_pain": "high-end millwork that needs careful patch-and-paint, tall solid-wood doors that drift, designer fixtures that need swap-outs without scratching adjacent finishes, and detailed exterior trim on stone facades",
        "weather_note": "mature tree canopy traps moisture against trim and decks; freeze-thaw seasons stress caulking and fence posts",
        "hero_sub": "Discreet, careful handyman service for Bayview Glen estate homes — premium finishes handled the right way.",
        "meta_desc": "Bayview Glen handyman service for luxury homes — drywall, door & trim repair, designer fixture swaps, painting touch-ups, deck and fence care. Licensed, insured.",
        "title": "Handyman Services in Bayview Glen | aMaximum Construction",
    },
    {
        "slug": "handyman-services-in-thornhill-woods",
        "category": "B",
        "city": "Thornhill Woods",
        "h1": "Handyman Services in Thornhill Woods",
        "neighbors_short": "Patterson, Dufferin Hill, Beverley Glen, central Thornhill, and Maple",
        "neighbors_faq": "Patterson, Dufferin Hill, Beverley Glen, Thornhill, and Maple",
        "housing": "modern executive homes, family townhomes, and 2000s subdivisions across the Bathurst corridor",
        "local_pain": "two-storey foyers with hanging fixtures that need re-aiming, builder-grade caulking that fails around year five, fence posts heaved by frost, and constant interior touch-ups in higher-traffic homes",
        "weather_note": "cold Vaughan winters and warm humid summers that work weatherstripping, exterior caulking, and door alignment",
        "hero_sub": "Reliable handyman service for Thornhill Woods family homes — clean visits, written estimates, no surprises.",
        "meta_desc": "Thornhill Woods handyman: drywall, door & window fixes, fixture install, TV mounting, deck and fence touch-ups, painting. Licensed, insured, written estimates.",
        "title": "Handyman Services in Thornhill Woods | aMaximum Construction",
    },
    {
        "slug": "handyman-services-in-glenville",
        "category": "B",
        "city": "Glenville",
        "h1": "Handyman Services in Glenville",
        "neighbors_short": "King City, Schomberg, Nobleton, Pottageville, and King Township",
        "neighbors_faq": "King City, Schomberg, Nobleton, Pottageville, and the rest of King Township",
        "housing": "country estates, hobby-farm properties, and rural detached homes on acreage",
        "local_pain": "long fences and gates exposed to wind and snow, deck boards on south-facing rural lots, well-pump and softener line touch-ups, mudroom doors with heavy use, and exterior trim on detached outbuildings",
        "weather_note": "open country exposure with stronger wind and snow load that wears fences, fascia, and exterior caulking faster than in town",
        "hero_sub": "Honest, reliable handyman visits to Glenville country properties and estate homes.",
        "meta_desc": "Glenville handyman service for rural and estate homes — drywall, doors, fixture install, painting, deck and fence repair. Licensed, insured, written estimates.",
        "title": "Handyman Services in Glenville | aMaximum Construction",
    },
    {
        "slug": "handyman-services-unionville",
        "category": "B",
        "city": "Unionville",
        "h1": "Handyman Services in Unionville",
        "neighbors_short": "Markham, Berczy Village, Cathedraltown, Milliken Mills, and Main Street Unionville",
        "neighbors_faq": "Markham, Berczy Village, Cathedraltown, Milliken Mills, and the Main Street heritage area",
        "housing": "heritage Main Street homes, modern executive subdivisions, and well-kept townhomes",
        "local_pain": "original wood doors and trim in heritage Main Street properties, plaster wall patches, settling porches, and constant fixture / TV mount installs in newer Berczy homes",
        "weather_note": "Markham's cold winters and warm humid summers that work caulking, weatherstripping, and heritage wood trim",
        "hero_sub": "Careful handyman visits for Unionville heritage homes and modern subdivisions alike.",
        "meta_desc": "Unionville handyman service for heritage and modern homes — drywall, door & trim repair, fixture install, painting, deck and fence care. Licensed, insured.",
        "title": "Handyman Services in Unionville | aMaximum Construction",
    },
    {
        "slug": "handyman-services-in-maple",
        "category": "B",
        "city": "Maple",
        "h1": "Handyman Services in Maple",
        "neighbors_short": "Vellore Village, Sonoma Heights, Patterson, Eagle Hills, and Woodbridge",
        "neighbors_faq": "Vellore Village, Sonoma Heights, Patterson, Eagle Hills, and Woodbridge",
        "housing": "family-friendly subdivisions, townhomes, and detached homes built since the 1990s",
        "local_pain": "builder-grade fixtures past the 10-year mark, fence panels heaved by frost, garage entry doors out of alignment, and constant TV / shelf install requests in family rooms and basements",
        "weather_note": "Vaughan winters that lift fence posts and crack exterior caulking, plus humid summers that swell wood doors",
        "hero_sub": "Reliable handyman visits across Maple — repairs, installs, and refresh work for busy family homes.",
        "meta_desc": "Maple handyman service: drywall, doors, faucet replacement, TV mounting, deck and fence repair, painting touch-ups. Licensed, insured, written estimates.",
        "title": "Handyman Services in Maple | aMaximum Construction",
    },
]


# ---------------------------------------------------------------------------
# Content generators
# ---------------------------------------------------------------------------

def services_bullets(c: dict) -> list[tuple[str, str]]:
    """6 bullet items for Category A 'Handyman Services We Provide in {city}'."""
    city = c["city"]
    return [
        ("Drywall Repair &amp; Patching",
         f"Nail pops, doorknob dents, water-stain patches, and full panel replacement — taped, mudded, sanded, and primed so the repair disappears under paint across {city} homes."),
        ("Door &amp; Window Adjustments",
         f"Interior doors that catch, exterior doors that won't latch, storm doors, weatherstripping, and window hardware fixes — common after {city}'s seasonal shifts."),
        ("Plumbing Fixtures",
         f"Faucet swaps, toilet replacements, shut-off valves, supply lines, and minor leak repairs — quick fixture-level work without rough-in plumbing scope."),
        ("Painting &amp; Caulking",
         f"Touch-ups, accent walls, trim re-paints, plus bathroom, kitchen, and exterior caulking refresh to keep moisture out of {city} homes year-round."),
        ("Mounting &amp; Fixtures",
         f"Stud-anchored TV mounting, ceiling fans, pendant lights, floating shelves, blinds, towel bars, and curtain rods — clean, plumb, and level."),
        ("General Repairs",
         f"Cabinet hardware, sticking drawers, weatherstripping, tile chips, deck-board swaps, and the small fence / gate fixes {city} owners put off — knocked out in one visit."),
    ]


def trust_bullets(c: dict) -> list[str]:
    """6-7 checkmark items for Category A trust list (no <a> tags here)."""
    city = c["city"]
    return [
        f"Background-checked, uniformed technicians who treat your {city} home like their own",
        "Fully insured — $2M liability coverage and WSIB clearance on every visit",
        "On-time arrival within a confirmed window — we respect your schedule",
        "Written estimate before any work begins — no surprise add-ons",
        "All debris removed and surfaces wiped down before we leave",
        f"Serving {city} and surrounding {c['neighbors_short']}",
    ]


def inline_faq_a(c: dict) -> list[tuple[str, str]]:
    """
    3-question inline FAQ for Category A pages.
    Q1 answer MUST contain the 3 existing <a> tags (drywall, plumbing, painting).
    Q3 answer MUST contain the existing <a> tag for electrical.
    """
    city = c["city"]
    q1 = f"What handyman tasks do you cover in {city}?"
    a1 = (
        f"Our {city} handyman team handles "
        f'<a href="/handyman-drywall-repair/">drywall repair</a>, '
        f"door and window installation, minor "
        f'<a href="/handyman-plumbing-services/">plumbing</a> '
        f"(fixture swaps, shut-off valves, supply lines), tile and caulking refresh, "
        f'<a href="/handyman-painting-services/">painting</a> touch-ups, '
        f"TV mounting, shelving, weatherstripping, and the small fix-it list "
        f"every {city} home accumulates."
    )
    q2 = f"How is handyman work priced in {city}?"
    a2 = (
        f"You can book us hourly for an open list of small tasks or as a flat-rate "
        f"job for clearly defined work. Either way you get a written estimate before "
        f"we start — no surprise charges. Minimum booking in {city} is two hours so a "
        f"visit is worth the trip."
    )
    q3 = f"Are your {city} handymen licensed and insured?"
    a3 = (
        f"Yes — every technician we send into {city} homes is covered by aMaximum "
        f"Construction's $2M liability policy and WSIB. Anything that legally needs "
        f"a trade ticket — such as full "
        f'<a href="/electrical-handyman-services/">electrical</a> '
        f"rough-in or plumbing behind the wall — is performed by our licensed "
        f"subcontractors, not the general handyman crew."
    )
    return [(q1, a1), (q2, a2), (q3, a3)]


def bottom_faq_a(c: dict) -> list[tuple[str, str]]:
    """
    10-question bottom FAQ for Category A.
    Q2 (services list) answer MUST contain the existing <a> tag for furniture-assembly.
    """
    city = c["city"]
    return [
        (
            f"How quickly can you book a handyman in {city}?",
            f"Most {city} jobs are scheduled within 3–7 business days. Urgent items "
            f"like a failed door lock, leaking shut-off, or storm damage are slotted "
            f"in sooner whenever the calendar allows — just flag the urgency when you call."
        ),
        (
            f"What handyman services do you offer in {city}?",
            f"We offer a full range of handyman services in {city} including: drywall "
            f"repair, painting, "
            f'<a href="/handyman-furniture-assembly/">furniture assembly</a>, '
            f"door and window adjustments, caulking, minor plumbing fixes, light "
            f"fixture installation, shelving, flooring repairs, weatherstripping, "
            f"and ongoing home maintenance."
        ),
        (
            f"How do you price handyman work in {city}?",
            f"For clearly defined tasks (mount a TV, replace a faucet, patch four "
            f"drywall holes) we quote a flat rate. For open to-do lists we charge "
            f"hourly with a two-hour minimum. Either way the price is written down "
            f"and approved before we touch a tool."
        ),
        (
            f"Can a handyman handle plumbing and electrical work in {city}?",
            f"We handle minor plumbing — faucet swaps, shut-off valves, toilet parts "
            f"— and minor electrical such as light fixtures, switches, and outlet "
            f"replacements that don't require a permit. Anything past that goes to a "
            f"licensed plumber or electrician on our team."
        ),
        (
            f"Do you mount TVs and shelving in {city} homes?",
            f"Yes — flat-screen TVs on drywall, concrete, and brick walls across "
            f"{city}. We locate studs or use the correct anchors, level the bracket, "
            f"and can run cables behind the wall for a clean finish. Floating "
            f"shelves, picture ledges, and full closet organizers also welcome."
        ),
        (
            f"Can you assemble furniture in {city}?",
            f"Yes — IKEA, Wayfair, office furniture, gym equipment, cribs, bunk beds, "
            f"and complex multi-piece assemblies. We bring the tools, follow the "
            f"manufacturer steps, and recycle the boxes on the way out."
        ),
        (
            f"What about exterior handyman work in {city}?",
            f"Exterior visits in {city} cover deck-board swaps, fence and gate "
            f"repair, caulking around windows and doors, gutter clear-outs, "
            f"weatherstripping, exterior paint touch-ups, and small concrete crack "
            f"repair to keep water out."
        ),
        (
            f"Can you handle multiple small jobs in one visit?",
            f"That's our most efficient {city} booking. A handyman half-day or full-"
            f"day knocks out an entire to-do list — hang pictures, patch walls, fix "
            f"squeaky doors, caulk windows, swap hardware, mount the TV — one visit, "
            f"one invoice."
        ),
        (
            f"Do you do drywall repair in {city}?",
            f"Yes — from pinholes to the larger openings a plumber or electrician "
            f"leaves behind. We patch, tape, mud, sand, and prime so the wall is "
            f"paint-ready, and match common spray or knockdown textures when needed."
        ),
        (
            f"What areas around {city} do you cover?",
            f"In addition to {city}, we serve {c['neighbors_faq']}. If you're nearby "
            f"and not sure, give us the postal code — we'll confirm before booking."
        ),
    ]


def faq_b(c: dict) -> list[tuple[str, str]]:
    """13-question bottom FAQ for Category B (no internal links in this block)."""
    city = c["city"]
    return [
        (
            f"What handyman services do you offer in {city}?",
            f"In {city} we cover drywall patching, painting touch-ups, door and "
            f"window adjustments, caulking and weatherstripping, minor plumbing "
            f"fixture work, light fixture installs, shelving, TV mounting, deck and "
            f"fence touch-ups, and general maintenance for {c['housing']}."
        ),
        (
            f"How do you price handyman jobs in {city}?",
            f"Defined jobs in {city} are flat-rated; open task lists are billed "
            f"hourly with a two-hour minimum. You see the written estimate and "
            f"approve scope before we begin — no surprise extras."
        ),
        (
            f"Can you tackle several small items in one {city} visit?",
            f"Yes — that's the most economical way to book us. One {city} handyman "
            f"half-day or full-day can handle your full list: patches, mounts, "
            f"caulking, hardware, hardware swaps, and finishing touches."
        ),
        (
            f"Do you do drywall repair in {city}?",
            f"Yes — small pinholes, doorknob impacts, water-stain patches and the "
            f"larger openings left by plumbing or electrical access work. We tape, "
            f"mud, sand, prime, and match the surrounding texture."
        ),
        (
            f"Can a handyman handle plumbing and electrical work in {city}?",
            f"We cover minor plumbing (faucet, shut-off valve, toilet parts) and "
            f"minor electrical (fixtures, switches, outlets) that don't require "
            f"permits. Anything bigger goes to a licensed trade on our team."
        ),
        (
            f"Do you assemble furniture in {city}?",
            f"Yes — IKEA, flat-pack, office furniture, gym kit, cribs, and complex "
            f"multi-piece units. We bring the tools and recycle the packaging."
        ),
        (
            f"Can you mount TVs and shelves in {city}?",
            f"We mount flat-screen TVs of all sizes on drywall, concrete, and brick "
            f"walls across {city}. Studs are located, brackets are levelled, and "
            f"cables can be hidden inside the wall for a clean finish."
        ),
        (
            f"How quickly can you book a {city} handyman visit?",
            f"Most {city} visits are scheduled within 3–7 business days. Urgent "
            f"items like a failed door lock or active leak are slotted in faster "
            f"whenever the calendar allows — flag the urgency when you call."
        ),
        (
            f"Do you do exterior handyman work in {city}?",
            f"Yes — deck-board swaps, fence and gate fixes, caulking around "
            f"windows and doors, gutter clear-outs, weatherstripping, exterior "
            f"paint touch-ups, and small concrete crack repairs across {city}."
        ),
        (
            f"Are your {city} handymen licensed and insured?",
            f"Every technician we send into a {city} home is covered by $2M "
            f"liability insurance and WSIB. Specialty work that legally requires a "
            f"trade licence is performed by our licensed subcontractors."
        ),
        (
            f"What kinds of {city} homes do you typically work in?",
            f"We work in {c['housing']} across {city}. Common tasks include "
            f"{c['local_pain']}."
        ),
        (
            f"How are your rates for handyman work in {city}?",
            f"Hourly rates start around the GTA market range, with a two-hour "
            f"minimum so the visit makes sense for both sides. Defined projects "
            f"get a flat price up front. We'll quote you specifically — no callout "
            f"surcharges hidden in the invoice."
        ),
        (
            f"Can I book same-week handyman service in {city}?",
            f"Often, yes — same-week slots open up regularly for {city}. Give us "
            f"your task list and preferred days and we'll confirm the next "
            f"available window."
        ),
    ]


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def render_ul(items: list, strong_pairs: bool = False, check: bool = False) -> str:
    parts = []
    for it in items:
        if strong_pairs:
            label, body = it
            parts.append(f"      <li><strong>{label}</strong> &mdash; {body}</li>")
        elif check:
            parts.append(f"      <li>&#10003; {it}</li>")
        else:
            parts.append(f"      <li>{it}</li>")
    return "<ul>\n" + "\n".join(parts) + "\n    </ul>"


def render_inline_faq(pairs: list[tuple[str, str]]) -> str:
    out = []
    for q, a in pairs:
        out.append(f"<h3>{q}</h3>")
        out.append(f"    <p>{a}</p>")
    return "\n    ".join(out)


def render_details_faq(pairs: list[tuple[str, str]]) -> str:
    out = []
    for q, a in pairs:
        out.append(
            "    <details class=\"faq-item\">\n"
            f"      <summary>{q}</summary>\n"
            f"      <p>{a}</p>\n"
            "    </details>"
        )
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Per-page updaters
# ---------------------------------------------------------------------------

def update_head(html: str, c: dict) -> str:
    """Update <title>, meta description, OG/Twitter title+desc. Schema FAQPage too."""
    city = c["city"]
    new_title = c["title"]
    new_desc = c["meta_desc"]

    html = re.sub(
        r"<title>.*?</title>",
        f"<title>{new_title}</title>",
        html, count=1, flags=re.DOTALL,
    )
    html = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{new_desc}">',
        html, count=1,
    )
    html = re.sub(
        r'<meta property="og:title" content="[^"]*">',
        f'<meta property="og:title" content="{new_title}">',
        html, count=1,
    )
    html = re.sub(
        r'<meta property="og:description" content="[^"]*">',
        f'<meta property="og:description" content="{new_desc}">',
        html, count=1,
    )
    html = re.sub(
        r'<meta name="twitter:title" content="[^"]*">',
        f'<meta name="twitter:title" content="{new_title}">',
        html, count=1,
    )
    html = re.sub(
        r'<meta name="twitter:description" content="[^"]*">',
        f'<meta name="twitter:description" content="{new_desc}">',
        html, count=1,
    )
    return html


def refresh_faq_schema(html: str, faq_pairs: list[tuple[str, str]]) -> str:
    """Rewrite the FAQPage mainEntity in JSON-LD with new Q&A text (plain text)."""
    def strip_tags(s: str) -> str:
        return re.sub(r"<[^>]+>", "", s).replace("  ", " ").strip()

    m = re.search(
        r'(\{\s*"@context":\s*"https://schema\.org",\s*"@type":\s*"FAQPage",\s*"mainEntity":\s*)\[.*?\](\s*\})',
        html, flags=re.DOTALL,
    )
    if not m:
        return html
    entries = []
    for q, a in faq_pairs:
        entries.append({
            "@type": "Question",
            "name": strip_tags(q),
            "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)},
        })
    new_list = json.dumps(entries, ensure_ascii=False, indent=4)
    return html[:m.start()] + m.group(1) + new_list + m.group(2) + html[m.end():]


def update_cat_a(slug: str, c: dict) -> bool:
    path = ROOT / slug / "index.html"
    src = path.read_text(encoding="utf-8")
    out = src

    out = update_head(out, c)

    # Hero subtitle
    out = re.sub(
        rf'(<h1>{re.escape(c["h1"])}</h1>\s*)<p>[^<]*</p>',
        rf'\1<p>{c["hero_sub"]}</p>',
        out, count=1,
    )

    # Intro paragraph (Reliable Handyman Services in {city})
    intro_new = (
        f"<p>aMaximum Construction's handyman team keeps {c['city']} homes in good "
        f"working order. We focus on {c['housing']}, where {c['weather_note']}. "
        f"Whether your list has one item or twenty, you get one insured crew, one "
        f"written estimate, and a clean finish — no half-done projects, no surprise "
        f"add-ons.</p>"
    )
    out = re.sub(
        r'(<h2>Reliable Handyman Services in [^<]+</h2>\s*</div>\s*<div style="padding:0 24px 16px;">\s*)<p>.*?</p>',
        lambda m: m.group(1) + intro_new,
        out, count=1, flags=re.DOTALL,
    )

    # Services bullet list
    bullets = services_bullets(c)
    new_ul = render_ul(bullets, strong_pairs=True)
    out = re.sub(
        r'(<h2>Handyman Services We Provide in [^<]+</h2>\s*</div>\s*<div style="padding:0 24px 16px;">\s*)<ul>.*?</ul>',
        lambda m: m.group(1) + new_ul,
        out, count=1, flags=re.DOTALL,
    )

    # Trust list
    trust_new = render_ul(trust_bullets(c), check=True)
    out = re.sub(
        r'(<h2>Why [^<]+ Residents Trust Our Handyman Team</h2>\s*</div>\s*<div style="padding:0 24px 16px;">\s*)<ul>.*?</ul>',
        lambda m: m.group(1) + trust_new,
        out, count=1, flags=re.DOTALL,
    )

    # Maintenance vs Renovation paragraph — preserve the existing GC link
    maint_new = (
        f"<p>Our handyman crew owns the small-job side of the list — repairs, "
        f"installations, finishing touches. For a full kitchen, bathroom, or "
        f"basement build-out in {c['city']}, our "
        f'<a href="{c["gc_href"]}">general contracting team</a> takes the project '
        f"over end-to-end with permits, trades coordination, and a single point "
        f"of contact. One call covers either path.</p>"
    )
    out = re.sub(
        r'(<h2>Home Maintenance vs\. Renovation in [^<]+</h2>\s*</div>\s*<div style="padding:0 24px 16px;">\s*)<p>.*?</p>',
        lambda m: m.group(1) + maint_new,
        out, count=1, flags=re.DOTALL,
    )

    # Inline FAQ (3 Q&A) — preserves links via inline_faq_a()
    inline_pairs = inline_faq_a(c)
    inline_html = render_inline_faq(inline_pairs)
    out = re.sub(
        r'(<h2>Frequently Asked Questions &mdash; Handyman [^<]+</h2>\s*</div>\s*<div style="padding:0 24px 16px;">\s*)<h3>.*?</p>(\s*</div>\s*</section>)',
        lambda m: m.group(1) + inline_html + m.group(2),
        out, count=1, flags=re.DOTALL,
    )
    # Some pages render `—` literally instead of `&mdash;`
    if "Frequently Asked Questions" in out:
        out = re.sub(
            r'(<h2>Frequently Asked Questions \u2014 Handyman [^<]+</h2>\s*</div>\s*<div style="padding:0 24px 16px;">\s*)<h3>.*?</p>(\s*</div>\s*</section>)',
            lambda m: m.group(1) + inline_html + m.group(2),
            out, count=1, flags=re.DOTALL,
        )

    # CTA section
    cta_new = (
        f'<div class="cta-section">\n'
        f'    <h2>Book Your {c["city"]} Handyman Visit</h2>\n'
        f'    <p>Send us the list — patches, mounts, caulking, fixtures — we\'ll '
        f'confirm scope, price, and a same-week window across {c["city"]}.</p>\n'
        f'    <a class="btn" href="/book-handy.html">BOOK NOW</a>\n'
        f'  </div>'
    )
    out = re.sub(
        r'<div class="cta-section">\s*<h2>Book a Handyman in [^<]+ Today</h2>.*?</div>',
        cta_new,
        out, count=1, flags=re.DOTALL,
    )

    # Bottom 10-Q FAQ — preserves furniture-assembly link via bottom_faq_a()
    bottom_pairs = bottom_faq_a(c)
    bottom_html = render_details_faq(bottom_pairs)
    out = re.sub(
        r'(<section class="island reveal" id="faq"[^>]*>.*?<div class="faq-list"[^>]*>)\s*'
        r'<details class="faq-item">.*?</details>\s*</div>\s*</section>',
        lambda m: m.group(1) + "\n    " + bottom_html + "\n  </div>\n</section>",
        out, count=1, flags=re.DOTALL,
    )

    # FAQPage schema — synced with inline FAQ (3 Q&A) which is what was there
    out = refresh_faq_schema(out, inline_pairs)

    if out == src:
        print(f"  [skip] {slug} — no changes (already updated?)")
        return False
    path.write_text(out, encoding="utf-8")
    print(f"  [ok]   {slug}")
    return True


def update_cat_b(slug: str, c: dict) -> bool:
    path = ROOT / slug / "index.html"
    src = path.read_text(encoding="utf-8")
    out = src

    out = update_head(out, c)

    # Hero subtitle
    out = re.sub(
        rf'(<h1>{re.escape(c["h1"])}</h1>\s*)<p>[^<]*</p>',
        rf'\1<p>{c["hero_sub"]}</p>',
        out, count=1,
    )

    # Intro
    intro_new = (
        f"<p>aMaximum Construction provides trusted handyman service across "
        f"{c['city']}. We work in {c['housing']}, where {c['weather_note']}. Our "
        f"crew shows up insured, brings the tools and materials, and finishes the "
        f"list cleanly — no half-done items, no surprise charges.</p>"
    )
    out = re.sub(
        r'(<h2>Reliable Handyman Services in [^<]+</h2>\s*</div>\s*<div style="padding:0 24px 16px;">\s*)<p>.*?</p>',
        lambda m: m.group(1) + intro_new,
        out, count=1, flags=re.DOTALL,
    )

    # Common handyman tasks list (no <a> tags inside)
    tasks = [
        ("Drywall Repair", "Pinholes, doorknob dents, water-stain patches, panel replacement"),
        ("Painting &amp; Touch-Ups", "Interior touch-ups, trim re-paints, accent walls, exterior spot fixes"),
        ("Fixture Installation", "Lights, ceiling fans, faucets, toilets, exhaust fans"),
        ("Door &amp; Window Adjustments", "Stuck doors, locks, weatherstripping, hardware swaps"),
        ("Furniture Assembly", "IKEA, flat-pack, office furniture, gym kit, multi-piece units"),
        ("Mounting &amp; Shelving", "TV mounts, floating shelves, picture ledges, blinds, curtain rods"),
        ("Minor Plumbing", "Faucets, shut-off valves, toilet parts, supply-line swaps"),
        ("Caulking &amp; Sealing", "Bathroom, kitchen, window, door, and exterior seal refresh"),
        ("General Repairs", "Cabinet hardware, sticking drawers, tile chips, deck-board swaps, small fence fixes"),
    ]
    new_ul = render_ul(tasks, strong_pairs=True)
    out = re.sub(
        r'(<h2>Common Handyman Tasks in [^<]+</h2>\s*</div>\s*<div style="padding:0 24px 16px;">\s*)<ul>.*?</ul>',
        lambda m: m.group(1) + new_ul,
        out, count=1, flags=re.DOTALL,
    )

    # Serving X and Surrounding Areas paragraph
    serving_new = (
        f"<p>Our handyman crew covers {c['city']} and nearby "
        f"{c['neighbors_short']}. On-time arrival, written estimate, clean job "
        f"site at the end. Whether you need a single fix or a long maintenance "
        f"list handled in one visit, we make the trip worthwhile.</p>"
    )
    out = re.sub(
        r'(<h2>Serving [^<]+ and Surrounding Areas</h2>\s*</div>\s*<div style="padding:0 24px 16px;">\s*)<p>.*?</p>',
        lambda m: m.group(1) + serving_new,
        out, count=1, flags=re.DOTALL,
    )

    # CTA
    cta_new = (
        f'<div class="cta-section">\n'
        f'    <h2>Book Your {c["city"]} Handyman Visit</h2>\n'
        f'    <p>Send us your {c["city"]} task list — patches, mounts, caulking, '
        f'fixtures. We confirm scope, price, and a same-week window.</p>\n'
        f'    <a class="btn" href="/book-handy.html">BOOK NOW</a>\n'
        f'  </div>'
    )
    out = re.sub(
        r'<div class="cta-section">\s*<h2>Book a Handyman in [^<]+</h2>.*?</div>',
        cta_new,
        out, count=1, flags=re.DOTALL,
    )

    # Bottom FAQ — replace ALL 13 <details> in the FAQ section with new 13
    faq_pairs = faq_b(c)
    bottom_html = render_details_faq(faq_pairs)
    out = re.sub(
        r'(<section class="island reveal" id="faq"[^>]*>.*?<div class="faq-list"[^>]*>)\s*'
        r'<details class="faq-item">.*?</details>\s*</div>\s*</section>',
        lambda m: m.group(1) + "\n    " + bottom_html + "\n  </div>\n</section>",
        out, count=1, flags=re.DOTALL,
    )

    # FAQPage schema currently holds the 3 city-specific Q&A — replace it with
    # the first 3 of our new FAQ for a tighter, accurate snippet.
    out = refresh_faq_schema(out, faq_pairs[:3])

    if out == src:
        print(f"  [skip] {slug} — no changes (already updated?)")
        return False
    path.write_text(out, encoding="utf-8")
    print(f"  [ok]   {slug}")
    return True


def update_cat_c(slug: str, c: dict) -> bool:
    """Toronto page — card-grid structure. Update title/meta + intro card text
    only, preserve all existing <a> tags."""
    path = ROOT / slug / "index.html"
    src = path.read_text(encoding="utf-8")
    out = src

    out = update_head(out, c)

    # H1 stays as-is. No structural changes — only text within sections that
    # do NOT carry internal links is light-touched. Toronto already reads as
    # a generic GTA hub; we leave card body text untouched to preserve the
    # painting link and avoid disturbing the unique card layout.

    if out == src:
        print(f"  [skip] {slug} — no changes")
        return False
    path.write_text(out, encoding="utf-8")
    print(f"  [ok]   {slug} (title/meta only)")
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    updated = 0
    for c in CITIES:
        slug = c["slug"]
        cat = c["category"]
        path = ROOT / slug / "index.html"
        if not path.exists():
            print(f"  [miss] {slug} — file not found, skipping")
            continue
        print(f"Updating ({cat}) {slug} ...")
        ok = False
        if cat == "A":
            ok = update_cat_a(slug, c)
        elif cat == "B":
            ok = update_cat_b(slug, c)
        elif cat == "C":
            ok = update_cat_c(slug, c)
        if ok:
            updated += 1
    print(f"\nDone. {updated}/{len(CITIES)} pages updated.")


if __name__ == "__main__":
    main()
