#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parent

TARGETS = [
    "plumbing-services-in-toronto",
    "plumbing-services-in-markham",
    "plumbing-services-in-vaughan",
    "plumbing-services-in-newmarket",
    "plumbing-services-in-richmond-hill",
]

CITY_BY_SLUG = {
    "plumbing-services-in-toronto": "Toronto",
    "plumbing-services-in-markham": "Markham",
    "plumbing-services-in-vaughan": "Vaughan",
    "plumbing-services-in-newmarket": "Newmarket",
    "plumbing-services-in-richmond-hill": "Richmond Hill",
}

PHONE_BY_CITY = {
    "Markham": "(289) 819-4777",
}


def phone_for_city(city: str) -> str:
    return PHONE_BY_CITY.get(city, "(647) 967-8555")


def keywords(city: str) -> list[str]:
    return [
        f"plumbing services {city}",
        f"plumber {city}",
        f"emergency plumber {city}",
        f"drain cleaning {city}",
        f"clogged drain service {city}",
        f"leak detection {city}",
        f"pipe repair {city}",
        f"water heater repair {city}",
        f"water heater installation {city}",
        f"toilet repair {city}",
        f"faucet installation {city}",
        f"sewer line repair {city}",
        f"sump pump installation {city}",
        f"backwater valve installation {city}",
        f"basement plumbing {city}",
        f"kitchen plumbing {city}",
        f"bathroom plumbing {city}",
        f"licensed plumber {city}",
        f"same day plumber {city}",
        f"24/7 plumber {city}",
    ]


def keyword_paragraph(city: str) -> str:
    terms = ", ".join(f"<strong>{k}</strong>" for k in keywords(city))
    return (
        "<p><strong>Local keyword cluster we cover in real projects:</strong> "
        f"{terms}.</p>"
    )


def replace_first(pattern: str, repl: str, text: str, *, flags: int = 0) -> str:
    return re.sub(pattern, repl, text, count=1, flags=flags)


def update_head(html: str, city: str) -> str:
    h1 = f"Plumbing Services in {city}"
    title = f"{h1} | aMaximum Construction"
    desc = (
        f"Licensed plumbing services in {city}. Faucet and fixture replacement, "
        f"leak repair, drain clearing, and rough-in plumbing. Free quotes from "
        f"aMaximum Construction."
    )

    html = replace_first(r"<title>.*?</title>", f"<title>{title}</title>", html, flags=re.DOTALL)

    html = replace_first(
        r'(<meta\s+[^>]*name=["\']description["\'][^>]*content=["\']).*?(["\'])',
        rf"\1{desc}\2",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    html = replace_first(
        r'(<meta\s+property=["\']og:title["\']\s+content=["\']).*?(["\']\s*/?>)',
        rf"\1{title}\2",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    html = replace_first(
        r'(<meta\s+name=["\']twitter:title["\']\s+content=["\']).*?(["\']\s*/?>)',
        rf"\1{title}\2",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    html = replace_first(
        r'(<meta\s+[^>]*property=["\']og:description["\'][^>]*content=["\']).*?(["\'])',
        rf"\1{desc}\2",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    html = replace_first(
        r'(<meta\s+[^>]*name=["\']twitter:description["\'][^>]*content=["\']).*?(["\'])',
        rf"\1{desc}\2",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return html


def update_hero(html: str, city: str) -> str:
    hero_p = (
        f"aMaximum Construction offers local homeowners in {city} professional "
        f"plumbing: faucet and fixture replacement, leak repair, drain clearing, "
        f"unclogging, and rough-in plumbing. As a local plumber, we handle "
        f"residential repairs and installations with dependable service tailored to "
        f"area homes. We provide {city} plumbing services for a wide range of "
        f"household plumbing needs. All jobs are pressure-tested and left clean "
        f"upon completion."
    )

    html = re.sub(
        r'(<div class="page-hero">\s*<h1[^>]*>.*?</h1>\s*)<p>.*?</p>',
        rf"\1<p>{hero_p}</p>",
        html,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )

    kw = keyword_paragraph(city)
    if "Local keyword cluster we cover in real projects:" in html:
        html = re.sub(
            r"<p><strong>Local keyword cluster we cover in real projects:</strong>.*?</p>",
            kw,
            html,
            count=1,
            flags=re.DOTALL,
        )
    else:
        html = re.sub(
            r"(<div class=\"page-hero\">\s*<h1[^>]*>.*?</h1>\s*<p>.*?</p>)",
            rf"\1\n{kw}",
            html,
            count=1,
            flags=re.DOTALL | re.IGNORECASE,
        )

    return html


def replace_h3_paragraph(html: str, heading: str, paragraph: str) -> str:
    pattern = re.escape(f"<h3>{heading}</h3>") + r"\s*<p>.*?</p>"
    repl = f"<h3>{heading}</h3>\n<p>{paragraph}</p>"
    return re.sub(pattern, repl, html, count=1, flags=re.DOTALL)


def update_sections(html: str, city: str) -> str:
    html = replace_first(
        r"(<section aria-label=\"Why choose us\".*?<h2>Why Choose aMaximum Construction\?</h2>\s*)<p>.*?</p>",
        (
            r"\1<p>We are a licensed and insured general contractor serving Toronto and the GTA since 2018. "
            f"Plumbing in Ontario is a strictly regulated trade, so homeowners should hire a licensed and insured plumbing contractor for this work. "
            f"When comparing providers in {city}, ask for proof of provincial licensing, WSIB coverage, at least $2 million in commercial liability insurance, and relevant project experience.</p>"
        ),
        html,
        flags=re.DOTALL,
    )

    html = replace_h3_paragraph(
        html,
        "Licensed &amp; Insured",
        "WSIB clearance, $2M liability insurance, and all permits handled by our licensed and insured professional plumbers. If you would like, we can provide proof of provincial licensing, WSIB coverage, and insurance before work begins. You are protected from start to finish.",
    )
    html = replace_h3_paragraph(
        html,
        "Clear Scope &amp; Fixed Price",
        "A detailed written quote before any work begins for transparent upfront pricing on high-quality plumbing services. Clear quoting supports reliable service and customer satisfaction. No hidden fees, no surprise invoices at the end.",
    )
    html = replace_h3_paragraph(
        html,
        "On Time &amp; On Budget",
        f"Milestone-based schedule with regular updates. We show up when we say we will and finish when we say we will, in a timely manner, with the fast scheduling and follow-up you expect from local {city} plumbers.",
    )
    html = replace_h3_paragraph(
        html,
        "Quality Workmanship",
        "Written warranty on all work. We use quality materials to handle all plumbing work with professional service, and back every job with a workmanship guarantee. Our experienced team aims to do an excellent job on every repair and plumbing installation.",
    )

    html = replace_first(
        r"(<section aria-label=\"Service types\".*?<h2>Plumbing Services We Offer</h2>\s*)<p>.*?</p>",
        (
            r"\1<p>We provide comprehensive plumbing solutions for residential and commercial clients, always adapted to your budget and requirements. "
            "Our team handles routine service, repairs, and installation work as part of complete plumbing support.</p>"
        ),
        html,
        flags=re.DOTALL,
    )

    html = replace_h3_paragraph(
        html,
        "Drain Cleaning",
        "Camera inspection, hydro-jetting, and snake clearing are part of our drain cleaning services and drain services for clogged, blocked, or slow drains. Hydro jetting is an advanced technique that uses high-pressure water to clear blockages and clean pipes effectively without causing damage. Clogged drains and slow drainage can point to buildup, roots, or line damage that may require drain repair. Video camera inspection helps identify buildup or sewer line issues before recommending drain unclogging or repair. Routine plumbing maintenance helps prevent backups, foul odors, and larger plumbing problems caused by buildup from grease, soap scum, hair, and mineral deposits, including unclogging drains as part of preventative and corrective maintenance for blocked drain issues.",
    )
    html = replace_h3_paragraph(
        html,
        "Pipe Repair &amp; Replacement",
        "Burst pipes, corroded lines, repiping - copper and PEX, plus emergency repairs for a pipe burst, frozen pipes, and water supply line issues. This is available as part of our emergency plumbing service when active leaks threaten your home, with 24/7 response for urgent problems like severe leaks.",
    )
    html = replace_h3_paragraph(
        html,
        "Fixture Installation",
        "Faucets, toilets, sinks, showers - supply and install, including repairs for leaky faucets, kitchen sink and bathroom sink issues, clogged toilet service, and fixture upgrades. For a clogged kitchen sink, service calls start by identifying whether the blockage is isolated to the fixture or connected to a larger drain problem. Recurring sink or toilet blockages can be signs of broader plumbing issues affecting the branch drain. We also handle common fixture repairs such as shut-off valve and fill valve replacements.",
    )
    html = replace_h3_paragraph(
        html,
        "Water Heater",
        f"Tank and tankless water heater installation, replacement, and water heater repair. Tankless water heaters are a space-saving option that provide consistent hot water, especially in homes where every square foot matters. Hard water, common in {city}, can cause sediment buildup, so annual maintenance such as flushing and replacing the sacrificial anode rod every 3 to 5 years helps extend system life; if a unit is over 10 years old and has a major failure, replacement is often the better choice.",
    )
    html = replace_h3_paragraph(
        html,
        "Rough-In Plumbing",
        "New bathroom, kitchen, basement - plumbing rough-in for renovations, with bathroom renovations often requiring careful venting, drainage planning, and code-compliant fixture placement. We also provide custom plumbing solutions for unique renovation layouts.",
    )

    html = replace_h3_paragraph(
        html,
        "Call or Book Online",
        f"Contact us for same-day or scheduled service, and for 24/7 emergency services in {city} when a plumbing emergency needs immediate response to help prevent property damage, including urgent issues such as a sewer backup or overflowing fixtures. We confirm an arrival window. These urgent issues can escalate within minutes and should be addressed right away.",
    )
    html = replace_h3_paragraph(
        html,
        "Diagnosis &amp; Quote",
        "We diagnose the issue, and an experienced plumber explains the recommended plumbing repairs and provides a fixed price before any work starts. Emergency plumbing situations are assessed quickly by licensed and insured plumbers, and repair costs depend on complexity, with typical rates often ranging from $200 to $300 per hour.",
    )
    html = replace_h3_paragraph(
        html,
        "Repair or Install",
        f"A licensed plumber in {city} completes the work to Ontario code standards.",
    )
    html = replace_h3_paragraph(
        html,
        "Test &amp; Guarantee",
        "We test the plumbing system before leaving, including checks for reliable drainage and water flow. Written warranty on all work.",
    )

    html = replace_first(
        r"(<section aria-label=\"Call to action\".*?<h2[^>]*>Ready to Get Started\?</h2>\s*)<p[^>]*>.*?</p>",
        (
            r"\1<p style=\"color:rgba(255,255,255,.9);margin-bottom:1.5rem;\">"
            "Get a free consultation and fixed quote - no obligation. "
            "We also handle sump pump installation and backwater valve installation to help reduce sewage backups and basement flooding during heavy rainstorms. "
            f"For backflow prevention, a sump pump and a backwater valve installed on the sewer line should remain accessible for inspection and cleaning, and the City of {city} may offer a rebate of up to $2,000."
            "</p>"
        ),
        html,
        flags=re.DOTALL,
    )

    return html


def update_faq(html: str, city: str) -> str:
    phone = phone_for_city(city)

    q1 = f"How much does a plumber cost in {city}?"
    a1 = (
        f"Plumbing service calls for plumbing services {city} customers request most often start around $150-$300 for diagnostics. "
        "Drain cleaning runs $250-$600. Pipe repairs vary by scope, and rates for plumbing repairs can vary based on the complexity of the job. "
        "More complex commercial plumbing services or after-hours work may be higher. We provide upfront quotes before any work."
    )
    a2 = (
        "Yes - we offer 24/7 emergency plumbing service for urgent issues such as sewer backup, clogged toilet overflow, burst pipes, and severe leaks. "
        f"These emergency repairs are handled in a timely manner by {city} plumbers. Call {phone} for urgent requests."
    )

    html = re.sub(
        r"<summary><h3>How much does a plumber cost in .*?</h3></summary>\s*<p>.*?</p>",
        f"<summary><h3>{q1}</h3></summary>\n      <p>{a1}</p>",
        html,
        count=1,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<summary><h3>Do you offer emergency plumbing\?</h3></summary>\s*<p>.*?</p>",
        "<summary><h3>Do you offer emergency plumbing?</h3></summary>\n      "
        f"<p>{a2}</p>",
        html,
        count=1,
        flags=re.DOTALL,
    )

    faq_json = f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "{q1}",
      "acceptedAnswer": {{"@type": "Answer", "text": "{a1}"}}
    }},
    {{
      "@type": "Question",
      "name": "Do you offer emergency plumbing?",
      "acceptedAnswer": {{"@type": "Answer", "text": "{a2}"}}
    }},
    {{
      "@type": "Question",
      "name": "Are your plumbers licensed in Ontario?",
      "acceptedAnswer": {{"@type": "Answer", "text": "Yes - all our plumbers hold a valid Ontario Certificate of Qualification (306A) and are fully insured."}}
    }},
    {{
      "@type": "Question",
      "name": "How do I know if I have a hidden leak?",
      "acceptedAnswer": {{"@type": "Answer", "text": "Signs include unexplained high water bills, damp drywall, mold smell, or water stains on ceilings. We use moisture meters and camera inspection to locate leaks."}}
    }},
    {{
      "@type": "Question",
      "name": "Can you fix the plumbing during a renovation?",
      "acceptedAnswer": {{"@type": "Answer", "text": "Absolutely - we coordinate plumbing rough-in and finishing with your renovation schedule. All work is permit-managed."}}
    }}
  ]
}}
</script>'''

    html = re.sub(
        r'<script type="application/ld\+json">\s*\{\s*"@context":\s*"https://schema.org",\s*"@type":\s*"FAQPage".*?</script>',
        faq_json,
        html,
        flags=re.DOTALL,
    )

    return html


def process_slug(slug: str) -> bool:
    path = ROOT / slug / "index.html"
    if not path.exists():
        print(f"[miss] {slug}")
        return False

    city = CITY_BY_SLUG[slug]
    src = path.read_text(encoding="utf-8")

    out = src
    out = update_head(out, city)
    out = update_hero(out, city)
    out = update_sections(out, city)
    out = update_faq(out, city)

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
