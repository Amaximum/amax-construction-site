"""link_blogs_services_locations.py

Mass-connects blogs <-> services <-> service+location pages.

Rules (per user):
- If a service already has a page WITHOUT location, use it as the hub.
- If a service has ONLY service+location pages, generate a NEW hub URL (auto-slug).
- Every blog is linked to an existing service (primarily via category).
- If a blog explicitly contains a location (URL or text), also link it to that service+location page.

This script is intentionally conservative:
- It only injects sections immediately BEFORE the existing <section id="reviews-embed"> block.
- It never touches Elfsight loader counts, rating widget, or reviews->faq ordering.

Usage:
  python link_blogs_services_locations.py --root . --apply
  python link_blogs_services_locations.py --root .            # dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# Keep in sync with site invariants expectations
ELFSIGHT_LOADER = '<script src="https://static.elfsight.com/platform/platform.js" defer></script>'
SITE_JS_VERSION = '20260314-1'
SITE_JS = f'<script src="/js/site.js?v={SITE_JS_VERSION}" defer></script>'
CSS_LINK = '<link rel="stylesheet" href="/css/styles.css">'

REVIEWS_APP_CLASS = 'elfsight-app-b029cad3-6f49-425c-9793-f556870797bb'
RATING_APP_CLASS = 'elfsight-app-3935cedc-67a1-44d8-b85e-f841374ae875'

STANDARD_NAV = """<div class=\"topbar-wrap shell\">
  <header class=\"topbar\" role=\"banner\">
    <a class=\"logo\" href=\"/\" aria-label=\"aMaximum Construction home\">
      <img src=\"/img/logo.png\" alt=\"aMaximum Construction\">
    </a>
    <div class=\"topbar-right\">
      <nav class=\"nav\" id=\"siteNav\" aria-label=\"Main navigation\">
        <a href=\"/\">Home</a>
        <a href=\"/#services\">Services</a>
        <a href=\"/locations/\">Locations</a>
        <a href=\"/blog/\">Blog</a>
        <a href=\"/portfolio/\">Portfolio</a>
        <a href=\"/#contact\">Contact</a>
      </nav>
      <a class=\"btn btn-primary btn-sm nav-quote\" href=\"/book-now/\">BOOK NOW</a>
      <button class=\"menu-btn\" id=\"menuBtn\" aria-label=\"Open menu\" aria-expanded=\"false\">&#9776;</button>
    </div>
  </header>
</div>"""

STANDARD_FOOTER_MIN = f"""<footer class=\"site-footer\">
  <div class=\"shell\">
    <div class=\"footer-cols\">
      <div class=\"footer-col footer-brand\">
        <a href=\"/\" class=\"footer-logo-link\"><img src=\"/img/logo.png\" alt=\"aMaximum Construction\" class=\"footer-logo\"></a>
        <p>Licensed and insured construction &amp; renovation services in Toronto &amp; GTA.</p>
        <a href=\"mailto:amaximumconstructioncorp@gmail.com\" class=\"footer-email\">amaximumconstructioncorp@gmail.com</a>
      </div>
      <div class=\"footer-col\">
        <h4>Company</h4>
        <ul>
          <li><a href=\"/\">Home</a></li>
          <li><a href=\"/portfolio/\">Portfolio</a></li>
          <li><a href=\"/blog/\">Blog</a></li>
          <li><a href=\"/#faq\">FAQ</a></li>
          <li><a href=\"/#contact\">Contact</a></li>
        </ul>
      </div>
    </div>
    <div class=\"footer-bar\">
      <span>&copy; 2026 aMaximum Construction. Licensed &amp; Insured.</span>
      <span>Toronto &amp; GTA</span>
    </div>
  </div>
</footer>"""

REVIEWS_EMBED_BLOCK = f"""<section id=\"reviews-embed\" class=\"shell\">\n  <div class=\"{REVIEWS_APP_CLASS}\"></div>\n</section>"""

RATING_FLOAT_WRAPPER = f"""<div id=\"rating-widget\" style=\"position:fixed;right:14px;bottom:14px;z-index:9999;max-width:220px;pointer-events:auto;\">\n  <div class=\"{RATING_APP_CLASS}\"></div>\n</div>"""


BLOG_CATEGORY_RE = re.compile(r'<span\s+class="(?:category|category-badge)">\s*([^<]+?)\s*</span>', re.I)
H1_RE = re.compile(r'<h1[^>]*>\s*([^<]+?)\s*</h1>', re.I)
TITLE_RE = re.compile(r'<title>\s*([^<]+?)\s*</title>', re.I)
SERVICE_TYPE_RE = re.compile(r'"serviceType"\s*:\s*"([^"]+)"', re.I)
AREA_SERVED_NAME_RE = re.compile(r'"areaServed"[\s\S]*?"name"\s*:\s*"([^"]+)"', re.I)

REVIEWS_SECTION_RE = re.compile(r"<section\b[^>]*\bid=['\"]reviews-embed['\"][^>]*>", re.I)


@dataclass(frozen=True)
class Location:
    name: str
    slug: str


@dataclass
class BlogPost:
    rel_dir: str
    url: str
    title: str
    category: str | None
    service_id: str | None
    location_slug: str | None


@dataclass
class ServicePage:
    rel_dir: str
    url: str
    service_id: str | None
    location_slug: str | None


@dataclass
class ServiceDef:
    service_id: str
    title: str
    homepage_href: str
    hub_url: str | None = None


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace')


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding='utf-8', newline='\n')


def rel_dir_from_index(root: Path, index_file: Path) -> str:
    rel = index_file.parent.relative_to(root).as_posix()
    return rel


def url_from_rel_dir(rel_dir: str) -> str:
    if not rel_dir:
        return '/'
    return f'/{rel_dir.strip("/")}/'


def slugify_service_title(title: str) -> str:
    s = title.lower()
    s = s.replace('&', ' and ')
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s.strip())
    s = re.sub(r'-{2,}', '-', s)

    # Mild normalization to match the user's examples.
    if s in {'handyman'}:
        s = 'handyman-services'
    if s in {'landscaping'}:
        s = 'landscaping-services'

    return s


def extract_title(html: str) -> str:
    m = H1_RE.search(html)
    if m:
        return html_unescape(m.group(1).strip())
    m = TITLE_RE.search(html)
    if m:
        return html_unescape(m.group(1).strip())
    return 'Untitled'


def html_unescape(s: str) -> str:
    return (
        s.replace('&amp;', '&')
         .replace('&quot;', '"')
         .replace('&#39;', "'")
         .replace('&lt;', '<')
         .replace('&gt;', '>')
    )


def extract_blog_category(html: str) -> str | None:
    m = BLOG_CATEGORY_RE.search(html)
    if not m:
        return None
    return html_unescape(m.group(1).strip())


def is_blog_page(html: str, rel_dir: str) -> bool:
    if rel_dir == 'blog':
        return False
    lower = html.lower()
    if 'class="page-blog"' in lower:
        return True
    if 'og:type" content="article"' in lower:
        return True
    if '"@type": "blogposting"' in lower:
        return True
    if '<div class="blog-hero"' in lower:
        return True
    return False


def is_service_page(html: str) -> bool:
    lower = html.lower()
    if '"@type": "localbusiness"' not in lower:
        return False
    if 'og:type" content="article"' in lower or '"@type": "blogposting"' in lower:
        return False
    return True


def classify_service_id(text: str) -> str | None:
    t = text.lower()

    # Order matters: specific before general.
    if 'deck railing' in t or 'deck railings' in t:
        return 'deck-railings'
    # Catch broader deck topics (maintenance, materials, etc.)
    if 'deck' in t:
        return 'deck-building'
    if 'deck builder' in t or 'deck building' in t or 'deck contractor' in t or 'deck construction' in t:
        return 'deck-building'
    if 'fence' in t or 'fencing' in t:
        return 'fence-installation'
    if 'bathroom' in t:
        return 'bathroom-renovation'
    if 'basement' in t:
        return 'basement-renovation'
    if 'home renovation' in t:
        return 'home-renovation'
    if 'renovation tips' in t:
        return 'home-renovation'
    if t.strip() in {'renovation', 'renovations'}:
        return 'home-renovation'
    if 'plumbing' in t:
        return 'plumbing'
    if 'canopy' in t or 'awning' in t:
        return 'canopy-awnings'
    if 'landscap' in t:
        return 'landscaping'
    if 'interlocking' in t or 'paver' in t or 'paving' in t:
        return 'interlocking-paving'
    if 'outdoor living' in t:
        return 'general-contractor'
    if 'general contractor' in t:
        return 'general-contractor'
    if 'general contracting' in t:
        return 'general-contractor'
    if t.strip() == 'guides':
        return 'general-contractor'
    if 'handyman' in t:
        return 'handyman'
    if 'carpentry' in t or 'carpenter' in t:
        return 'carpentry'
    if 'demolition' in t:
        return 'demolition'
    if 'excavation' in t:
        return 'excavation'
    if 'electrical' in t:
        return 'electrical'
    if 'painting' in t:
        return 'painting'
    if 'christmas light' in t or 'holiday light' in t:
        return 'christmas-lights'

    return None


def detect_location_slug(
    *,
    rel_dir: str,
    html: str,
    locations: list[Location],
) -> str | None:
    # URL-based signals
    rel_lower = rel_dir.lower()
    for loc in locations:
        slug = loc.slug
        if f'-in-{slug}' in rel_lower:
            return slug
        if rel_lower.endswith(f'-{slug}'):
            return slug
        if f'/{slug}/' in rel_lower:
            # Rare: location in a path segment
            return slug

    # Text-based signals (title/h1/body)
    hay = (extract_title(html) + ' ' + html)[:50000].lower()
    for loc in locations:
        name = loc.name.lower()
        if re.search(rf'\b{re.escape(name)}\b', hay, flags=re.I):
            return loc.slug

    return None


def extract_service_type_text(html: str) -> str:
    m = SERVICE_TYPE_RE.search(html)
    if m:
        return m.group(1)
    return ''


def extract_area_served_name(html: str) -> str | None:
    m = AREA_SERVED_NAME_RE.search(html)
    if m:
        return m.group(1).strip()
    return None


def load_locations() -> list[Location]:
    # Import is safe (no side effects unless __main__).
    import generate_service_pages as gsp  # type: ignore

    locs: list[Location] = []
    for item in getattr(gsp, 'LOCATIONS', []):
        name = item.get('name')
        slug = item.get('slug')
        if name and slug:
            locs.append(Location(name=name, slug=slug))
    return locs


def parse_homepage_services(root: Path) -> list[ServiceDef]:
    html = read_text(root / 'index.html')
    # Match only the card titles.
    card_re = re.compile(r'<h3>\s*<a\s+href="([^"]+)">\s*([^<]+?)\s*</a>\s*</h3>', re.I)
    seen: set[str] = set()
    services: list[ServiceDef] = []

    for href, title in card_re.findall(html):
        title = html_unescape(title.strip())
        if title in seen:
            continue
        seen.add(title)
        service_id = classify_service_id(title) or slugify_service_title(title)
        services.append(ServiceDef(service_id=service_id, title=title, homepage_href=href.strip()))

    # Include services that exist sitewide but may not be on the homepage cards.
    # This enables mapping blog categories like "Home Renovation" and generating a non-location hub.
    homepage_ids = {s.service_id for s in services}
    if 'home-renovation' not in homepage_ids:
        services.append(ServiceDef(service_id='home-renovation', title='Home Renovation', homepage_href=''))

    return services


def hub_exists(root: Path, hub_url: str) -> bool:
    if not hub_url.startswith('/'):
        return False
    rel = hub_url.strip('/')
    p = root / rel / 'index.html'
    return p.exists()


def resolve_hub_url(root: Path, svc: ServiceDef, locations: list[Location]) -> str:
    href = svc.homepage_href
    # If homepage link points to a non-location page and it exists, treat it as hub.
    if href.startswith('/') and hub_exists(root, href):
        href_dir = href.strip('/')
        is_locationish = any(
            href_dir.endswith(f'-{loc.slug}') or f'-in-{loc.slug}' in href_dir
            for loc in locations
        )
        if not is_locationish:
            return href

    # Otherwise generate a new hub URL (auto-slug).
    slug = slugify_service_title(svc.title)
    return f'/{slug}/'


def build_hub_page(
    *,
    hub_url: str,
    service_title: str,
    service_id: str,
    location_links: list[tuple[str, str]],  # (url, label)
    related_blogs: list[tuple[str, str]],  # (url, title)
) -> str:
    canonical = f'https://amaximumconstruction.com{hub_url}'

    # Very small service copy; avoid inventing too much.
    desc = f"{service_title} in Toronto & GTA. Licensed, insured, code-aligned service. Free quotes. aMaximum Construction.".replace('  ', ' ')

    locations_ul = "\n".join([f'    <li><a href="{u}">{label}</a></li>' for (u, label) in location_links])
    if not locations_ul:
        locations_ul = '    <li><a href="/locations/">All Locations &rarr;</a></li>'

    blogs_ul = "\n".join([f'    <li><a href="{u}">{html_escape(title)}</a></li>' for (u, title) in related_blogs])

    related_section = ''
    if blogs_ul:
        related_section = f"""
<section id="related-articles" class="shell" style="padding:32px 0 0;">
  <h2 style="font-size:1.25rem;font-weight:700;color:#121826;margin-bottom:16px;">Related Articles</h2>
  <ul style="display:flex;flex-direction:column;gap:10px;list-style:disc;padding-left:18px;margin:0;">
{blogs_ul}
  </ul>
</section>
"""

    locations_section = f"""
<section id="service-areas" class="shell" style="padding:32px 0 0;">
  <h2 style="font-size:1.25rem;font-weight:700;color:#121826;margin-bottom:16px;">{service_title} Near You</h2>
  <ul style="display:flex;flex-wrap:wrap;gap:8px 24px;list-style:none;padding:0;margin:0;">
{locations_ul}
  </ul>
</section>
"""

    faq = f"""
<section class="island reveal" id="faq" aria-label="Frequently asked questions">
  <span class="shine" aria-hidden="true"></span>
  <div class="section-head">
    <h2>Frequently Asked Questions</h2>
    <p>Common questions about {service_title} in Toronto and the GTA.</p>
  </div>
  <div class="faq-list">
    <details class="faq-item">
      <summary>Do you provide free quotes?</summary>
      <p>Yes. We provide free measurement and written quotes for {service_title} projects in Toronto and the GTA.</p>
    </details>
    <details class="faq-item">
      <summary>Do you handle permits and code requirements?</summary>
      <p>We build and install to Ontario Building Code requirements and can advise on permits and inspection requirements based on your municipality.</p>
    </details>
    <details class="faq-item">
      <summary>How long does a typical project take?</summary>
      <p>Timelines vary by scope and materials. After a site visit we provide a clear schedule before work begins.</p>
    </details>
  </div>
</section>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{html_escape(desc)}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{html_escape(service_title)} | aMaximum Construction">
  <meta property="og:description" content="{html_escape(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="aMaximum Construction">
  <link rel="canonical" href="{canonical}">
  <title>{html_escape(service_title)} | aMaximum Construction</title>
  {ELFSIGHT_LOADER}
  {SITE_JS}
  {CSS_LINK}
  <script type="application/ld+json">
  [
    {{
      "@context": "https://schema.org",
      "@type": "LocalBusiness",
      "name": "aMaximum Construction",
      "url": "{canonical}",
      "email": "amaximumconstructioncorp@gmail.com",
      "serviceType": "{html_escape(service_title)}",
      "areaServed": {{
        "@type": "AdministrativeArea",
        "name": "Toronto & GTA",
        "addressRegion": "ON",
        "addressCountry": "CA"
      }}
    }},
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://amaximumconstruction.com/"}},
        {{"@type": "ListItem", "position": 2, "name": "{html_escape(service_title)}", "item": "{canonical}"}}
      ]
    }}
  ]
  </script>
  <link rel="icon" href="/img/logo.png" type="image/png">
  <link rel="apple-touch-icon" href="/img/logo.png">
</head>
<body>
{STANDARD_NAV}

<div class="page-hero">
  <h1>{html_escape(service_title)}</h1>
  <p>Serving Toronto and the Greater Toronto Area</p>
</div>

<div class="container">
  <div class="content">
    <h2>{html_escape(service_title)} Services</h2>
    <p>aMaximum Construction provides {html_escape(service_title.lower())} services across Toronto and the GTA with clear scope, tidy execution, and code-aligned results.</p>
  </div>
  <div class="cta-section">
    <h2>Get a Quote</h2>
    <p>Free measurement and quote — serving Toronto and the GTA.</p>
    <a class="btn" href="/book-now/">BOOK NOW</a>
  </div>
</div>

{locations_section}
{related_section}

{REVIEWS_EMBED_BLOCK}
{faq}

{STANDARD_FOOTER_MIN}

{RATING_FLOAT_WRAPPER}
</body>
</html>
"""


def html_escape(s: str) -> str:
    return (
        s.replace('&', '&amp;')
         .replace('<', '&lt;')
         .replace('>', '&gt;')
         .replace('"', '&quot;')
    )


def discover_pages(root: Path, locations: list[Location]) -> tuple[list[BlogPost], list[ServicePage]]:
    blogs: list[BlogPost] = []
    service_pages: list[ServicePage] = []

    skip_dirs = {
        '.git', '.vscode', '__pycache__',
        'img', 'css', 'js',
    }

    for index_file in root.rglob('index.html'):
        rel_parts = index_file.relative_to(root).parts
        if not rel_parts:
            continue
        if any(part in skip_dirs for part in rel_parts):
            continue
        # Skip deeply nested assets-like structures under img etc (already covered).

        rel_dir = rel_dir_from_index(root, index_file)
        html = read_text(index_file)

        if is_blog_page(html, rel_dir):
            title = extract_title(html)
            category = extract_blog_category(html)
            service_id = classify_service_id(category or '') or classify_service_id(title)
            location_slug = detect_location_slug(rel_dir=rel_dir, html=html, locations=locations)
            blogs.append(
                BlogPost(
                    rel_dir=rel_dir,
                    url=url_from_rel_dir(rel_dir),
                    title=title,
                    category=category,
                    service_id=service_id,
                    location_slug=location_slug,
                )
            )
            continue

        if is_service_page(html):
            service_text = extract_service_type_text(html) + ' ' + extract_title(html)
            service_id = classify_service_id(service_text)

            # Prefer structured areaServed name when available
            loc_name = extract_area_served_name(html)
            location_slug = None
            if loc_name:
                for loc in locations:
                    if loc.name.lower() == loc_name.lower():
                        location_slug = loc.slug
                        break
            if not location_slug:
                location_slug = detect_location_slug(rel_dir=rel_dir, html=html, locations=locations)

            service_pages.append(
                ServicePage(
                    rel_dir=rel_dir,
                    url=url_from_rel_dir(rel_dir),
                    service_id=service_id,
                    location_slug=location_slug,
                )
            )

    return blogs, service_pages


def inject_before_reviews(html: str, block_html: str) -> str:
    m = REVIEWS_SECTION_RE.search(html)
    if not m:
        return html
    start = m.start(0)
    return html[:start] + block_html + "\n" + html[start:]


def build_related_blogs_block(items: list[tuple[str, str]]) -> str:
    if not items:
        return ''
    lis = "\n".join([f'    <li><a href="{u}">{html_escape(t)}</a></li>' for (u, t) in items])
    return f"""
<section id="related-blogs" class="shell" style="padding:32px 0 0;">
  <h2 style="font-size:1.25rem;font-weight:700;color:#121826;margin-bottom:12px;">Related Blog Posts</h2>
  <ul style="margin:0;padding-left:18px;display:flex;flex-direction:column;gap:10px;">
{lis}
  </ul>
</section>
""".strip('\n')


def build_blog_service_links_block(service_title: str, hub_url: str, location_label: str | None, location_url: str | None) -> str:
    loc_line = ''
    if location_label and location_url:
        loc_line = f'  <li><a href="{location_url}">{html_escape(service_title)} in {html_escape(location_label)}</a></li>\n'

    return f"""
<section id="service-links" class="shell" style="padding:32px 0 0;">
  <h2 style="font-size:1.25rem;font-weight:700;color:#121826;margin-bottom:12px;">Related Service</h2>
  <ul style="margin:0;padding-left:18px;display:flex;flex-direction:column;gap:10px;">
    <li><a href="{hub_url}">{html_escape(service_title)} Services</a></li>
{loc_line}  </ul>
</section>
""".strip('\n')


def upsert_sitemap_urls(sitemap_path: Path, urls: Iterable[str], apply: bool) -> int:
    if not sitemap_path.exists():
        return 0
    xml = read_text(sitemap_path)
    added = 0
    for u in urls:
        loc = f'https://amaximumconstruction.com{u}'
        if f'<loc>{loc}</loc>' in xml:
            continue
        # Insert before closing tag.
        insert = f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>monthly</changefreq>\n  </url>\n"
        xml = xml.replace('</urlset>', insert + '</urlset>')
        added += 1
    if apply and added:
        write_text(sitemap_path, xml)
    return added


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--max-related', type=int, default=6)
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    apply = bool(args.apply)

    locations = load_locations()

    services = parse_homepage_services(root)
    for svc in services:
        svc.hub_url = resolve_hub_url(root, svc, locations)

    # Discover pages first
    blogs, service_pages = discover_pages(root, locations)

    # Build lookup maps
    loc_by_slug = {l.slug: l for l in locations}

    # Service title lookup from homepage card titles
    service_title_by_id = {s.service_id: s.title for s in services}

    # Build service+location page lookup
    svc_loc_to_url: dict[tuple[str, str], str] = {}
    for sp in service_pages:
        if not sp.service_id or not sp.location_slug:
            continue
        svc_loc_to_url[(sp.service_id, sp.location_slug)] = sp.url

    # Group blogs by service and by (service, location)
    blogs_by_service: dict[str, list[BlogPost]] = {}
    blogs_by_service_loc: dict[tuple[str, str], list[BlogPost]] = {}

    for bp in blogs:
        if not bp.service_id:
            continue
        blogs_by_service.setdefault(bp.service_id, []).append(bp)
        if bp.location_slug:
            blogs_by_service_loc.setdefault((bp.service_id, bp.location_slug), []).append(bp)

    # 1) Ensure hubs exist (create missing)
    created_hubs: list[str] = []
    for svc in services:
        hub_url = svc.hub_url
        if not hub_url:
            continue
        if hub_exists(root, hub_url):
            continue

        # Build location links for this service
        loc_links: list[tuple[str, str]] = []
        for loc in locations:
            u = svc_loc_to_url.get((svc.service_id, loc.slug))
            if u:
                loc_links.append((u, loc.name))

        # Related blogs: prefer general (no location), then any
        related: list[tuple[str, str]] = []
        for bp in blogs_by_service.get(svc.service_id, []):
            if not bp.location_slug:
                related.append((bp.url, bp.title))
        if not related:
            related = [(bp.url, bp.title) for bp in blogs_by_service.get(svc.service_id, [])]
        related = related[: args.max_related]

        hub_html = build_hub_page(
            hub_url=hub_url,
            service_title=svc.title,
            service_id=svc.service_id,
            location_links=loc_links,
            related_blogs=related,
        )

        hub_file = root / hub_url.strip('/') / 'index.html'
        if apply:
            hub_file.parent.mkdir(parents=True, exist_ok=True)
            write_text(hub_file, hub_html)
        created_hubs.append(hub_url)

    # 2) Update hubs (insert/replace service areas + related articles)
    # Conservative approach: only inject blocks if missing.
    updated_files: list[Path] = []

    for svc in services:
        if not svc.hub_url or not hub_exists(root, svc.hub_url):
            continue
        hub_file = root / svc.hub_url.strip('/') / 'index.html'
        html = read_text(hub_file)

        # Build location links
        loc_links: list[tuple[str, str]] = []
        for loc in locations:
            u = svc_loc_to_url.get((svc.service_id, loc.slug))
            if u:
                loc_links.append((u, loc.name))

        # Build related articles (service-level)
        related: list[tuple[str, str]] = []
        for bp in blogs_by_service.get(svc.service_id, []):
            if not bp.location_slug:
                related.append((bp.url, bp.title))
        related = related[: args.max_related]

        # If hub already has a service-areas section, leave it as-is.
        changed = False
        if 'id="service-areas"' not in html:
            locations_section = build_hub_page(
                hub_url=svc.hub_url,
                service_title=svc.title,
                service_id=svc.service_id,
                location_links=loc_links,
                related_blogs=related,
            )
            # build_hub_page returns a full doc; we only want the sections. So skip.
            # (We only auto-create full hubs; existing hubs are left untouched to avoid template drift.)
            pass

        # For hubs we created in this run, content already includes the right sections.
        if changed and apply:
            write_text(hub_file, html)
            updated_files.append(hub_file)

    # 3) Inject related blogs into service+location pages
    injected_service_pages = 0
    for sp in service_pages:
        if not sp.service_id:
            continue
        if sp.rel_dir == 'book-now':
            continue
        page_file = root / sp.rel_dir / 'index.html'
        html = read_text(page_file)
        if 'id="related-blogs"' in html:
            continue
        if not REVIEWS_SECTION_RE.search(html):
            continue

        items: list[tuple[str, str]] = []
        if sp.location_slug:
            for bp in blogs_by_service_loc.get((sp.service_id, sp.location_slug), []):
                items.append((bp.url, bp.title))

        # Fill with general service blogs if needed
        if len(items) < args.max_related:
            for bp in blogs_by_service.get(sp.service_id, []):
                if bp.location_slug:
                    continue
                items.append((bp.url, bp.title))
                if len(items) >= args.max_related:
                    break

        block = build_related_blogs_block(items)
        if not block:
            continue
        new_html = inject_before_reviews(html, block)
        if new_html != html:
            injected_service_pages += 1
            if apply:
                write_text(page_file, new_html)

    # 4) Inject service links into blog posts
    injected_blog_pages = 0
    for bp in blogs:
        if not bp.service_id:
            continue
        page_file = root / bp.rel_dir / 'index.html'
        html = read_text(page_file)
        if 'id="service-links"' in html:
            continue
        if not REVIEWS_SECTION_RE.search(html):
            continue

        # Resolve hub for the service
        svc = next((s for s in services if s.service_id == bp.service_id), None)
        if not svc or not svc.hub_url:
            continue

        service_title = service_title_by_id.get(bp.service_id, svc.title)
        location_label = None
        location_url = None
        if bp.location_slug and bp.location_slug in loc_by_slug:
            location_label = loc_by_slug[bp.location_slug].name
            location_url = svc_loc_to_url.get((bp.service_id, bp.location_slug))

        block = build_blog_service_links_block(service_title, svc.hub_url, location_label, location_url)
        new_html = inject_before_reviews(html, block)
        if new_html != html:
            injected_blog_pages += 1
            if apply:
                write_text(page_file, new_html)

    # 5) Update sitemap with newly created hubs
    sitemap_added = upsert_sitemap_urls(root / 'sitemap.xml', created_hubs, apply=apply)

    # Report
    print('=== link_blogs_services_locations ===')
    print(f'Root: {root}')
    print(f'Apply: {apply}')
    print(f'Locations: {len(locations)}')
    print(f'Services(from homepage cards): {len(services)}')
    print(f'Blogs discovered: {len(blogs)}')
    print(f'Service pages discovered: {len(service_pages)}')
    print(f'Hubs created: {len(created_hubs)}')
    if created_hubs:
        for u in created_hubs:
            print(f'  + {u}')
    print(f'Injected related blogs into service+location pages: {injected_service_pages}')
    print(f'Injected service links into blog pages: {injected_blog_pages}')
    print(f'Sitemap entries added: {sitemap_added}')

    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
