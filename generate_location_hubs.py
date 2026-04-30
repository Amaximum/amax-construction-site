from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LOCATIONS_ROOT = ROOT / "locations"
ASSET_VERSION = "20260429n"
SITE_URL = "https://amaximumconstruction.com"

ACTIVE_LOCATION_RE = re.compile(r'<span class="location-card location-card-active">([^<]+)</span>', re.I)
H1_RE = re.compile(r"<h1>([^<]+)</h1>", re.I)
META_DESCRIPTION_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]+)"', re.I)

EXCLUDED_LABELS = {
    "GTA",
    "General Contractor Near Me",
    "General Contractor Services",
    "General Contractor Services 2",
    "Toronto GTA",
}

LOCATION_ALIASES = {
    "Basement & Bathroom North York": "North York",
    "Basement & Bathroom Richmond Hill": "Richmond Hill",
    "Basement Renovation Toronto": "Toronto",
    "Deck Builder Newmarket": "Newmarket",
    "Deck Builder Richmond Hill": "Richmond Hill",
    "Deck Builder Toronto": "Toronto",
    "Deck Railings Toronto": "Toronto",
    "Etobicoke (Alt)": "Etobicoke",
    "Fence Installer Aurora": "Aurora",
    "Markham (Alt)": "Markham",
    "North York (Alt)": "North York",
    "Paving Richmond Hill": "Richmond Hill",
    "Railing Builder Markham": "Markham",
    "Railing Builder Richmond Hill": "Richmond Hill",
    "Railing Installer East York": "East York",
    "Railing Vaughan": "Vaughan",
    "Scarborough (Alt)": "Scarborough",
    "Toronto (Specialists)": "Toronto",
}

SERVICE_RULES: list[tuple[re.Pattern[str], str, str, list[str]]] = [
    (
        re.compile(r"^(basement-and-bathroom-renovation-in-|basement-bathroom-renovation-)", re.I),
        "Basement & Bathroom Renovation",
        "Combined basement finishing and bathroom renovation solutions in {location}.",
        [r"^basement-and-bathroom-renovation-in-", r"^basement-bathroom-renovation-"],
    ),
    (
        re.compile(r"^basement-renovation", re.I),
        "Basement Renovation",
        "Dedicated basement renovation options for homes in {location}.",
        [r"^basement-renovation-service-in-", r"^basement-renovation-in-"],
    ),
    (
        re.compile(r"^bathrooms?-renovation", re.I),
        "Bathroom Renovation",
        "Bathroom remodeling and upgrade services currently published for {location}.",
        [r"^bathroom-renovation-", r"^bathrooms-renovation-"],
    ),
    (
        re.compile(r"^deck-(builder|contractor)", re.I),
        "Deck Building",
        "Deck design, build, and replacement services available in {location}.",
        [r"^deck-contractor-", r"^deck-builder-", r"^deck-builder-in-"],
    ),
    (
        re.compile(r"^deck-railing", re.I),
        "Deck Railings",
        "Deck railing installation and replacement pages for {location}.",
        [r"^deck-railing-installer-in-", r"^deck-railing-builder-", r"^deck-railing-installation-in-", r"^deck-railing-", r"^deck-railings-"],
    ),
    (
        re.compile(r"^fence-(contractor|installer)", re.I),
        "Fence Installation",
        "Fence installation and repair services currently available in {location}.",
        [r"^fence-contractor-in-", r"^fence-installer-"],
    ),
    (
        re.compile(r"^handyman-service|^handyman-services", re.I),
        "Handyman",
        "General handyman work and small-project support in {location}.",
        [r"^handyman-service-in-", r"^handyman-services-in-", r"^handyman-services-"],
    ),
    (
        re.compile(r"^general-contractor", re.I),
        "General Contractor",
        "Full-scope construction planning and project management in {location}.",
        [r"^general-contractor-in-"],
    ),
    (
        re.compile(r"^carpenter-services", re.I),
        "Carpentry",
        "Custom carpentry, trim, framing, and finish work in {location}.",
        [r"^carpenter-services-"],
    ),
    (
        re.compile(r"^demolition-service|^demolition-services", re.I),
        "Demolition",
        "Selective demolition and tear-out services for projects in {location}.",
        [r"^demolition-service-in-", r"^demolition-service-", r"^demolition-services-"],
    ),
    (
        re.compile(r"^interlocking-stone-services|^interlock-paving-contractor", re.I),
        "Interlocking & Paving",
        "Interlocking stone, paving, and hardscape pages for {location}.",
        [r"^interlocking-stone-services-in-", r"^interlocking-stone-services-", r"^interlock-paving-contractor-"],
    ),
    (
        re.compile(r"^home-renovation|^renovation-services", re.I),
        "Home Renovation",
        "Whole-home and interior renovation services already published for {location}.",
        [r"^home-renovation-", r"^renovation-services-in-"],
    ),
    (
        re.compile(r"^christmas-lights-installation", re.I),
        "Christmas Lights",
        "Seasonal Christmas light installation pages available in {location}.",
        [r"^christmas-lights-installation-in-"],
    ),
]

SERVICE_ORDER = [
    "General Contractor",
    "Home Renovation",
    "Bathroom Renovation",
    "Basement Renovation",
    "Basement & Bathroom Renovation",
    "Deck Building",
    "Deck Railings",
    "Fence Installation",
    "Interlocking & Paving",
    "Carpentry",
    "Demolition",
    "Handyman",
    "Christmas Lights",
]


@dataclass(frozen=True)
class ServicePage:
    location: str
    location_slug: str
    service: str
    slug: str
    title: str
    description: str
    path: str
    preference_index: int


def slugify(value: str) -> str:
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def title_case_words(value: str) -> str:
    return " ".join(part.capitalize() for part in value.split())


def extract_h1(text: str, fallback: str) -> str:
    match = H1_RE.search(text)
    return html.unescape(match.group(1).strip()) if match else fallback


def extract_meta_description(text: str) -> str:
    match = META_DESCRIPTION_RE.search(text)
    return html.unescape(match.group(1).strip()) if match else ""


def normalize_location(raw_label: str, h1: str) -> str | None:
    raw_label = html.unescape(raw_label).strip()
    if raw_label in EXCLUDED_LABELS:
        return None
    if raw_label in LOCATION_ALIASES:
        return LOCATION_ALIASES[raw_label]

    h1_match = re.search(r"\bin\s+([A-Za-z][A-Za-z\- ]+)$", h1)
    if h1_match:
        candidate = h1_match.group(1).strip()
        if candidate not in EXCLUDED_LABELS and "GTA" not in candidate:
            return candidate

    if raw_label.endswith(" (Alt)") or raw_label.endswith(" (Specialists)"):
        return raw_label.rsplit(" (", 1)[0]

    if "GTA" in raw_label:
        return None

    if any(keyword in raw_label for keyword in ["General Contractor", "Deck Builder", "Deck Railings", "Railing ", "Fence Installer", "Basement Renovation"]):
        return None

    return raw_label


def classify_service(slug: str, title: str, location: str) -> tuple[str, str, int]:
    for pattern, service, description, preferences in SERVICE_RULES:
        if pattern.search(slug):
            for index, preferred in enumerate(preferences):
                if re.search(preferred, slug, re.I):
                    return service, description.format(location=location), index
            return service, description.format(location=location), len(preferences)

    trimmed = re.sub(r"\s+in\s+" + re.escape(location) + r"$", "", title).strip()
    trimmed = re.sub(r"\bServices?\b$", "", trimmed).strip()
    trimmed = re.sub(r"\bService\b$", "", trimmed).strip()
    return trimmed, f"Dedicated {trimmed.lower()} page for {location}.", 99


def collect_service_pages() -> dict[str, list[ServicePage]]:
    grouped: dict[str, dict[str, ServicePage]] = {}

    for path in sorted(ROOT.glob("*/index.html")):
        folder = path.parent.name
        if folder == "locations":
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        active_match = ACTIVE_LOCATION_RE.search(text)
        if not active_match:
            continue

        title = extract_h1(text, folder)
        location = normalize_location(active_match.group(1), title)
        if not location:
            continue

        location_slug = slugify(location)
        meta_description = extract_meta_description(text)
        service, fallback_description, preference_index = classify_service(folder, title, location)
        description = meta_description or fallback_description
        service_page = ServicePage(
            location=location,
            location_slug=location_slug,
            service=service,
            slug=folder,
            title=title,
            description=description,
            path=f"/{folder}/",
            preference_index=preference_index,
        )

        service_map = grouped.setdefault(location, {})
        current = service_map.get(service)
        if current is None or (service_page.preference_index, service_page.slug) < (current.preference_index, current.slug):
            service_map[service] = service_page

    return {
        location: sorted(
            service_map.values(),
            key=lambda item: (
                SERVICE_ORDER.index(item.service) if item.service in SERVICE_ORDER else len(SERVICE_ORDER),
                item.service,
            ),
        )
        for location, service_map in sorted(grouped.items())
    }


def top_footer_locations(grouped_pages: dict[str, list[ServicePage]]) -> list[tuple[str, str]]:
    ranked = sorted(
        grouped_pages.items(),
        key=lambda item: (-len(item[1]), item[0]),
    )
    return [(location, slugify(location)) for location, _ in ranked[:8]]


def build_breadcrumb_schema(location: str | None = None, location_slug: str | None = None) -> dict[str, object]:
    items: list[dict[str, object]] = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": f"{SITE_URL}/",
        },
        {
            "@type": "ListItem",
            "position": 2,
            "name": "Locations",
            "item": f"{SITE_URL}/locations/",
        },
    ]
    if location and location_slug:
        items.append(
            {
                "@type": "ListItem",
                "position": 3,
                "name": location,
                "item": f"{SITE_URL}/locations/{location_slug}/",
            }
        )
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


def build_item_list_schema(name: str, entries: list[tuple[str, str]]) -> dict[str, object]:
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index,
                "name": entry_name,
                "url": f"{SITE_URL}{entry_path}",
            }
            for index, (entry_name, entry_path) in enumerate(entries, start=1)
        ],
    }


def location_footer_html(grouped_pages: dict[str, list[ServicePage]]) -> str:
    location_items = "\n".join(
        f'          <li><a href="/locations/{location_slug}/">{html.escape(location)}</a></li>'
        for location, location_slug in top_footer_locations(grouped_pages)
    )
    return f"""
<footer class="site-footer">
  <div class="shell">
    <div class="footer-cols">
      <div class="footer-col footer-brand">
        <a href="/" class="footer-logo-link"><img src="/img/logo.png" alt="aMaximum Construction" class="footer-logo"></a>
        <p>Licensed and insured construction and renovation services in Toronto and the GTA.</p>
      </div>
      <div class="footer-col">
        <h2>Services</h2>
        <ul>
          <li><a href="/deck-builder/">Deck Building</a></li>
          <li><a href="/deck-railings-toronto/">Deck Railings</a></li>
          <li><a href="/fence-contractor-in-toronto/">Fence Installation</a></li>
          <li><a href="/bathroom-renovation/">Bathroom Renovation</a></li>
          <li><a href="/basement-renovation-service-in-toronto/">Basement Renovation</a></li>
          <li><a href="/handyman-service-in-toronto/">Handyman</a></li>
          <li><a href="/general-contractor-in-toronto/">General Contractor</a></li>
          <li><a href="/home-renovation/">Home Renovation</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h2>Locations</h2>
        <ul>
{location_items}
          <li><a href="/locations/">All Locations &rarr;</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h2>Company</h2>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/portfolio/">Portfolio</a></li>
          <li><a href="/blog/">Blog</a></li>
          <li><a href="/#contact">Contact</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bar">
      <span>&copy; 2026 aMaximum Construction. Licensed &amp; Insured.</span>
      <span>Toronto &amp; GTA</span>
      <span class="footer-friends">Friends: <a href="https://besttorontodecks.com/" rel="nofollow noopener noreferrer" target="_blank">besttorontodecks.com</a> <span aria-hidden="true">&middot;</span> <a href="https://npak.ca/" rel="nofollow noopener noreferrer" target="_blank">npak.ca</a> <span aria-hidden="true">&middot;</span> <a href="https://amaxtattoo.com/" rel="nofollow noopener noreferrer" target="_blank">amaxtattoo.com</a></span>
    </div>
  </div>
</footer>
<div id="rating-widget" style="position:fixed;right:14px;bottom:14px;z-index:9999;max-width:220px;pointer-events:auto;">
  <div class="elfsight-app-3935cedc-67a1-44d8-b85e-f841374ae875"></div>
</div>
""".strip()


def page_shell(title: str, meta_description: str, canonical_path: str, schema_objects: list[dict[str, object]], body: str) -> str:
    escaped_title = html.escape(title)
    escaped_meta = html.escape(meta_description)
    schema_json = json.dumps(schema_objects, ensure_ascii=False, indent=2)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{escaped_meta}">
  <meta name="robots" content="index, follow">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{escaped_title}">
  <meta property="og:description" content="{escaped_meta}">
  <meta property="og:url" content="{SITE_URL}{canonical_path}">
  <meta property="og:site_name" content="aMaximum Construction">
  <link rel="canonical" href="{SITE_URL}{canonical_path}">
  <title>{escaped_title}</title>
  <script src="https://static.elfsight.com/platform/platform.js" defer></script>
  <script src="/js/site.js?v={ASSET_VERSION}" defer></script>
  <link rel="stylesheet" href="/css/styles.css?v={ASSET_VERSION}">
  <script type="application/ld+json">
{schema_json}
  </script>
  <link rel="icon" href="/img/logo.png" type="image/png">
  <link rel="apple-touch-icon" href="/img/logo.png">
</head>
<body>
  <div class="topbar-wrap shell">
    <header class="topbar" role="banner">
      <a class="logo" href="/" aria-label="aMaximum Construction home">
        <img src="/img/logo.png" alt="aMaximum Construction">
      </a>
      <div class="topbar-right">
        <nav class="nav" id="siteNav" aria-label="Main navigation">
          <a href="/">Home</a>
          <a href="/#services">Services</a>
          <a href="/locations/">Locations</a>
          <a href="/blog/">Blog</a>
          <a href="/portfolio/">Portfolio</a>
          <a href="/#contact">Contact</a>
        </nav>
        <a class="btn btn-primary btn-sm nav-quote" href="/book-now/">BOOK NOW</a>
        <button class="menu-btn" id="menuBtn" aria-label="Open menu" aria-expanded="false">&#9776;</button>
      </div>
    </header>
  </div>
{body}
</body>
</html>
"""


def build_location_page(location: str, pages: list[ServicePage], grouped_pages: dict[str, list[ServicePage]]) -> str:
    location_slug = slugify(location)
    service_cards = "\n".join(
        f'''          <a href="{page.path}" class="card">\n            <h3>{html.escape(page.service)}</h3>\n            <p>{html.escape(page.description)}</p>\n          </a>'''
        for page in pages
    )
    service_names = ", ".join(page.service for page in pages)
    meta_description = (
        f"Browse the services currently published for {location}, including {service_names[:120]}"
        if len(service_names) <= 120
        else f"Browse the services currently published for {location}."
    )
    faq_items = [
        (
            f"Which services are currently available in {location}?",
            f"This location page currently lists {len(pages)} published service pages for {location}: {service_names}.",
        ),
        (
            f"Do these links open {location}-specific service pages?",
            f"Yes. Every card on this page opens a service page that is specifically published for {location}, not a different city or regional proxy page.",
        ),
        (
            f"How do I request a quote in {location}?",
            f"Use the BOOK NOW button to request a quote for your project in {location}. We can review the service you need and confirm the next steps for your address.",
        ),
    ]
    faq_html = "\n".join(
        f'''    <details class="faq-item">\n      <summary>{html.escape(question)}</summary>\n      <p>{html.escape(answer)}</p>\n    </details>'''
        for question, answer in faq_items
    )
    schema_objects = [
        build_breadcrumb_schema(location, location_slug),
        build_item_list_schema(
            f"Services in {location}",
            [(page.service, page.path) for page in pages],
        ),
    ]
    body = f"""
  <main>
    <div class="shell">
      <section class="page-hero">
        <h1>Construction &amp; Renovation Services in {html.escape(location)}</h1>
        <p>Only the service pages currently published for {html.escape(location)} are shown below. Each card opens the service page for this location only.</p>
        <a href="/book-now/" class="btn">Request Quote in {html.escape(location)}</a>
      </section>

      <section>
        <h2>Available Services in {html.escape(location)}</h2>
        <p>{len(pages)} service pages are currently available for this location.</p>
        <div class="cards">
{service_cards}
        </div>
      </section>

      <section>
        <h2>How This Location Page Works</h2>
        <p>This page only shows services that already have a dedicated {html.escape(location)} page in the site. If a service is not listed here, it does not currently have a published {html.escape(location)} page.</p>
      </section>

      <section class="cta-section">
        <h2>Need Help in {html.escape(location)}?</h2>
        <p style="margin: 16px 0; font-size: 18px;">Tell us what service you need and we will point you to the right team.</p>
        <a href="/book-now/" class="btn">BOOK NOW</a>
      </section>
    </div>
  </main>

  <section id="reviews-embed" class="shell">
    <div class="elfsight-app-b029cad3-6f49-425c-9793-f556870797bb"></div>
  </section>
  <section class="island reveal" id="faq" aria-label="Frequently asked questions">
    <span class="shine" aria-hidden="true"></span>
    <div class="section-head">
      <h2>Frequently Asked Questions</h2>
      <p>Common questions about available services in {html.escape(location)}.</p>
    </div>
    <div class="faq-list">
{faq_html}
    </div>
  </section>

  {location_footer_html(grouped_pages)}
""".strip()
    return page_shell(
        title=f"Construction & Renovation Services in {location} | aMaximum Construction",
        meta_description=meta_description,
        canonical_path=f"/locations/{location_slug}/",
        schema_objects=schema_objects,
        body=body,
    )


def build_locations_index(grouped_pages: dict[str, list[ServicePage]]) -> str:
    cards = []
    for location, pages in grouped_pages.items():
        preview = ", ".join(page.service for page in pages[:3])
        if len(pages) > 3:
            preview += ", and more"
        cards.append(
            f'''          <a href="/locations/{slugify(location)}/" class="card">\n            <h3>{html.escape(location)}</h3>\n            <p>{len(pages)} services currently published for this location.</p>\n            <p>{html.escape(preview)}</p>\n          </a>'''
        )
    cards_html = "\n".join(cards)
    faq_items = [
        (
            "What happens when I click a location?",
            "Each location opens its own page that shows only the service pages currently published for that specific area.",
        ),
        (
            "Why is one location missing from this directory?",
            "A location only appears here when at least one service page has already been published for that location.",
        ),
        (
            "Can different locations show different services?",
            "Yes. Each location page is based on the service pages currently available for that location, so the service list can vary from one area to another.",
        ),
    ]
    faq_html = "\n".join(
        f'''    <details class="faq-item">\n      <summary>{html.escape(question)}</summary>\n      <p>{html.escape(answer)}</p>\n    </details>'''
        for question, answer in faq_items
    )
    schema_objects = [
        build_breadcrumb_schema(),
        build_item_list_schema(
            "All Service Locations",
            [(location, f"/locations/{slugify(location)}/") for location in grouped_pages],
        ),
    ]
    body = f"""
  <main>
    <div class="shell">
      <section class="page-hero">
        <h1>All Service Locations</h1>
        <p>Browse every location that currently has at least one published service page. Clicking a location opens a page that shows only the services available there.</p>
      </section>

      <section>
        <h2>All Published Locations</h2>
        <p>{len(grouped_pages)} locations currently have at least one dedicated service page in the site.</p>
        <div class="cards">
{cards_html}
        </div>
      </section>

      <section>
        <h2>How the Directory Works</h2>
        <p>Each location card above opens a dedicated location page. That page only shows the service pages already published for that exact location.</p>
      </section>

      <section class="cta-section">
        <h2>Need a Quote?</h2>
        <p style="margin: 16px 0; font-size: 18px;">Choose your location first, then open the service page that matches your project.</p>
        <a href="/book-now/" class="btn">BOOK NOW</a>
      </section>
    </div>
  </main>

  <section id="reviews-embed" class="shell">
    <div class="elfsight-app-b029cad3-6f49-425c-9793-f556870797bb"></div>
  </section>
  <section class="island reveal" id="faq" aria-label="Frequently asked questions">
    <span class="shine" aria-hidden="true"></span>
    <div class="section-head">
      <h2>Frequently Asked Questions</h2>
      <p>Common questions about the location directory.</p>
    </div>
    <div class="faq-list">
{faq_html}
    </div>
  </section>

  {location_footer_html(grouped_pages)}
""".strip()
    return page_shell(
        title="All Service Locations | aMaximum Construction",
        meta_description="Browse all locations that currently have published aMaximum Construction service pages.",
        canonical_path="/locations/",
        schema_objects=schema_objects,
        body=body,
    )


def write_location_pages(grouped_pages: dict[str, list[ServicePage]]) -> None:
    LOCATIONS_ROOT.mkdir(parents=True, exist_ok=True)

    for location, pages in grouped_pages.items():
        location_dir = LOCATIONS_ROOT / slugify(location)
        location_dir.mkdir(parents=True, exist_ok=True)
        (location_dir / "index.html").write_text(
            build_location_page(location, pages, grouped_pages),
            encoding="utf-8",
        )

    (LOCATIONS_ROOT / "index.html").write_text(
        build_locations_index(grouped_pages),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate dedicated location hub pages from existing service pages.")
    parser.add_argument("--write", action="store_true", help="Write generated HTML files into the locations directory.")
    args = parser.parse_args()

    grouped_pages = collect_service_pages()
    summary = {
        "location_count": len(grouped_pages),
        "locations": {location: [page.service for page in pages] for location, pages in grouped_pages.items()},
    }
    print(json.dumps(summary, ensure_ascii=True, indent=2))

    if args.write:
        write_location_pages(grouped_pages)
        print(f"Wrote {len(grouped_pages)} location pages plus locations/index.html")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())