"""restructure_hubs.py

Hub <-> Location <-> Blog structural fix across all 18 service hubs.

Rules:
  - 1 Hub per service (non-location). NEVER create new pages.
  - Hub primary CTA must point to /book-*.html (never to a location).
  - Hub `#locations` grid must list EVERY existing location page of that service.
  - Hub `#related-articles` must list ONLY non-location blogs of that service.
  - Location page `#related-blogs` shows blogs tied to that city; falls back
    to the service's general blogs.
  - Blog page `#service-links` points to its hub (and its city's location page if any).

Usage:
  python restructure_hubs.py            # dry-run report
  python restructure_hubs.py --apply    # apply fixes
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

# Known city slugs across the site. A captured tail that matches one of these
# is treated as a real city; anything else stays as a blog.
CITIES: dict[str, str] = {
    'toronto': 'Toronto',
    'north-york': 'North York',
    'east-york': 'East York',
    'scarborough': 'Scarborough',
    'etobicoke': 'Etobicoke',
    'markham': 'Markham',
    'richmond-hill': 'Richmond Hill',
    'vaughan': 'Vaughan',
    'woodbridge': 'Woodbridge',
    'aurora': 'Aurora',
    'newmarket': 'Newmarket',
    'thornhill': 'Thornhill',
    'thornhill-woods': 'Thornhill Woods',
    'king-city': 'King City',
    'kleinburg': 'Kleinburg',
    'concord': 'Concord',
    'maple': 'Maple',
    'mississauga': 'Mississauga',
    'oakville': 'Oakville',
    'burlington': 'Burlington',
    'hamilton': 'Hamilton',
    'brampton': 'Brampton',
    'bradford': 'Bradford',
    'east-gwillimbury': 'East Gwillimbury',
    'schomberg': 'Schomberg',
    'forest-hill': 'Forest Hill',
    'bayview-glen': 'Bayview Glen',
    'glenville': 'Glenville',
    'whitchurch-stouffville': 'Whitchurch-Stouffville',
    'unionville': 'Unionville',
    'nobleton': 'Nobleton',
    'king-creek': 'King Creek',
    'pickering': 'Pickering',
}


# Each service entry:
#   hub_dir, label, book_url
#   location_patterns: list of regex strings; the (?P<city>...) group is
#     validated against CITIES (slug -> pretty name).
#   blog_keywords: substrings that classify a non-location, non-hub dir
#     as a blog of this service.
#   blog_excludes: substrings that override blog_keywords (avoid false matches).
SERVICES: list[dict] = [
    {
        'hub_dir': 'deck-railings',
        'label': 'Deck Railings',
        'book_url': '/book-railing.html',
        'location_patterns': [
            r'^deck-railing-installer-(?:in-)?(?P<city>[a-z][a-z0-9-]+)$',
            r'^deck-railing-builder-(?P<city>[a-z][a-z0-9-]+)$',
            r'^deck-railing-installation-in-(?P<city>[a-z][a-z0-9-]+)$',
            r'^deck-railing-(?P<city>[a-z][a-z0-9-]+)$',
            r'^deck-railings-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['railing'],
        'blog_excludes': [],
    },
    {
        'hub_dir': 'deck-builder',
        'label': 'Deck Building',
        'book_url': '/book-deck.html',
        'location_patterns': [
            r'^deck-builder-(?:in-)?(?P<city>[a-z][a-z0-9-]+)$',
            r'^deck-contractor-(?:in-)?(?P<city>[a-z][a-z0-9-]+)$',
            r'^custom-decks-(?P<city>[a-z][a-z0-9-]+)$',
            r'^amazing-decks-in-(?P<city>[a-z][a-z0-9-]+)$',
            r'^expert-deck-building-in-(?P<city>[a-z][a-z0-9-]+)$',
            r'^wood-deck-repair-in-(?P<city>[a-z][a-z0-9-]+)$',
            r'^building-a-deck-in-(?P<city>[a-z][a-z0-9-]+)$',
            r'^building-a-small-deck-in-(?P<city>[a-z][a-z0-9-]+)$',
            r'^is-it-cheaper-to-build-your-own-deck-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['deck', 'trex', 'rainescape'],
        'blog_excludes': ['railing', 'privacy-screen-deck'],
    },
    {
        'hub_dir': 'fence-contractor-in-toronto',
        'label': 'Fence Installation',
        'book_url': '/book-fence.html',
        'location_patterns': [
            r'^fence-contractor-(?:in-)?(?P<city>[a-z][a-z0-9-]+)$',
            r'^fence-installer-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['fence', 'privacy-screen'],
        'blog_excludes': [],
    },
    {
        'hub_dir': 'bathroom-renovation',
        'label': 'Bathroom Renovation',
        'book_url': '/book-bathroom.html',
        'location_patterns': [
            r'^bathroom-renovation-(?:in-)?(?P<city>[a-z][a-z0-9-]+)$',
            r'^bathrooms-renovation-(?:in-)?(?P<city>[a-z][a-z0-9-]+)$',
            r'^interior-bathroom-renovation-(?P<city>[a-z][a-z0-9-]+)$',
            # combos shared with basement; we list them here so they appear under bathroom hub too.
            r'^basement-(?:and-)?bathroom-renovation-(?:in-)?(?P<city>[a-z][a-z0-9-]+)$',
            r'^basement-bathroom-renovation-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['bathroom'],
        'blog_excludes': [],
    },
    {
        'hub_dir': 'basement-renovation-service-in-toronto',
        'label': 'Basement Renovation',
        'book_url': '/book-basement.html',
        'location_patterns': [
            r'^basement-renovation-service-in-(?P<city>[a-z][a-z0-9-]+)$',
            r'^basement-renovation-(?P<city>[a-z][a-z0-9-]+)$',
            r'^basement-renovation-in-(?P<city>[a-z][a-z0-9-]+)$',
            r'^best-basement-renovation-service-(?:in-)?(?P<city>[a-z][a-z0-9-]+)$',
            # combos
            r'^basement-(?:and-)?bathroom-renovation-(?:in-)?(?P<city>[a-z][a-z0-9-]+)$',
            r'^basement-bathroom-renovation-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['basement'],
        'blog_excludes': [],
    },
    {
        'hub_dir': 'handyman-plumbing-services',
        'label': 'Plumbing',
        'book_url': '/book-plumbing.html',
        'location_patterns': [
            r'^plumbing-services-in-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['plumbing'],
        'blog_excludes': [],
    },
    {
        'hub_dir': 'canopy',
        'label': 'Canopy & Awnings',
        'book_url': '/book-canopy.html',
        'location_patterns': [
            r'^canopy-installation-in-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['canopy', 'awning'],
        'blog_excludes': [],
    },
    {
        'hub_dir': 'landscaping-services-toronto',
        'label': 'Landscaping',
        'book_url': '/book-landscaping.html',
        'location_patterns': [
            r'^landscaping-services-(?P<city>[a-z][a-z0-9-]+)$',
            r'^landscaping-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['landscap', 'outdoor-living', 'outdoor living', 'backyard', 'oasis'],
        'blog_excludes': [],
    },
    {
        'hub_dir': 'general-contractor-in-toronto',
        'label': 'General Contractor',
        'book_url': '/book-contractor.html',
        'location_patterns': [
            r'^general-contractor-(?:in-)?(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['general-contractor', 'contractor', 'small-contractor', 'general-contracting', 'general contracting', 'construction-project', 'construction project'],
        'blog_excludes': ['general-contractor-in-', 'general-contractor-services'],
    },
    {
        'hub_dir': 'handyman-service-in-toronto',
        'label': 'Handyman',
        'book_url': '/book-handy.html',
        'location_patterns': [
            r'^handyman-service-in-(?P<city>[a-z][a-z0-9-]+)$',
            r'^handyman-services-in-(?P<city>[a-z][a-z0-9-]+)$',
            r'^handyman-services-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['handyman'],
        'blog_excludes': [],
    },
    {
        'hub_dir': 'interlocking-paver-services',
        'label': 'Interlocking',
        'book_url': '/book-interlock.html',
        'location_patterns': [
            r'^interlocking-stone-services-(?:in-)?(?P<city>[a-z][a-z0-9-]+)$',
            r'^interlock-paving-contractor-(?:in-)?(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['interlock', 'paver', 'paving'],
        'blog_excludes': [],
    },
    {
        'hub_dir': 'carpenter-services',
        'label': 'Carpentry',
        'book_url': '/book-carpentry.html',
        'location_patterns': [
            r'^carpenter-services-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['carpenter', 'carpentry'],
        'blog_excludes': [],
    },
    {
        'hub_dir': 'electrical-handyman-services',
        'label': 'Electrical',
        'book_url': '/book-electrical.html',
        'location_patterns': [
            r'^electrical-services-in-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['electrical'],
        'blog_excludes': [],
    },
    {
        'hub_dir': 'handyman-painting-services',
        'label': 'Painting',
        'book_url': '/book-painting.html',
        'location_patterns': [
            r'^painting-services-in-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['painting'],
        'blog_excludes': [],
    },
    {
        'hub_dir': 'demolition-services',
        'label': 'Demolition',
        'book_url': '/book-demolition.html',
        'location_patterns': [
            r'^demolition-service-(?:in-)?(?P<city>[a-z][a-z0-9-]+)$',
            r'^demolition-services-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['demolition'],
        'blog_excludes': [],
    },
    {
        'hub_dir': 'excavation-services',
        'label': 'Excavation',
        'book_url': '/book-excavation.html',
        'location_patterns': [
            r'^excavation-services-in-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['excavation'],
        'blog_excludes': [],
    },
    {
        'hub_dir': 'home-renovation',
        'label': 'Home Renovation',
        'book_url': '/book-renovation.html',
        'location_patterns': [
            r'^home-renovation-(?P<city>[a-z][a-z0-9-]+)$',
            r'^renovation-services-in-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['home-renovation', 'home-reno', 'renovation', 'renovating', 'renovate'],
        'blog_excludes': ['bathroom', 'basement'],
    },
    {
        'hub_dir': 'christmas-lights-installation-toronto-gta',
        'label': 'Christmas Lights',
        'book_url': '/book-christmas.html',
        'location_patterns': [
            r'^christmas-lights-installation-in-(?P<city>[a-z][a-z0-9-]+)$',
            r'^professional-christmas-lights-installer-(?P<city>[a-z][a-z0-9-]+)$',
        ],
        'blog_keywords': ['christmas', 'holiday-light'],
        'blog_excludes': [],
    },
]

# All hub dirs (for quick membership tests)
HUB_DIRS: set[str] = {s['hub_dir'] for s in SERVICES}

# Dirs we never touch / classify (infrastructure & non-service pages)
SKIP_DIRS: set[str] = {
    '.git', '.github', '.venv', '.venv-1', '.claude', '__pycache__',
    'img', 'css', 'js', 'tools', 'sitemap', 'citations', 'locations',
    'portfolio', 'services', 'book-now', 'thank-you-page',
    'client-testimonials', 'company-policy-of-amaximum-construction',
    'our-work-process', 'why-choose-us', 'what-we-do',
}

# Legacy non-location "duplicate-hub" slugs. These are NOT blogs and should
# NOT appear in related-articles. They are old generic service pages without
# a city; we leave them in place but exclude them from cross-linking.
DUPLICATE_HUB_SLUGS: set[str] = {
    'basement-renovation',
    'fence-installation',
    'general-contractor',
    'general-contractor-services',
    'general-contractor-services-2',
    'general-contractor-services-near-me',
    'handyman-services',
    'landscaping-services',
    'paving-company',
    'renovation-service',
    'deck-builder-gta',
    # Verified by content inspection (verify_blog_candidates.py): these
    # use og:type=website + LocalBusiness schema and have NO article markers
    # (no blog-hero, no article-body, no @type:Article). They are legacy
    # service-area landings or a blog index page, not articles.
    '1-basement-renovation-near-me',
    'amaximum-deck-builder-blog',
    'handyman-drywall-repair',
    'handyman-furniture-assembly',
    'renovation-services-in-toronto-gta',
    'privacy-screen-installation-in-north-york',
}

# HTML templates ----------------------------------------------------------

LOCATIONS_SECTION_RE = re.compile(
    r'<section\b[^>]*\bid="locations"[^>]*>.*?</section>\s*',
    re.DOTALL | re.IGNORECASE,
)
RELATED_ARTICLES_SECTION_RE = re.compile(
    r'<section\b[^>]*\bid="related-articles"[^>]*>.*?</section>\s*',
    re.DOTALL | re.IGNORECASE,
)
RELATED_BLOGS_SECTION_RE = re.compile(
    r'<section\b[^>]*\bid="related-blogs"[^>]*>.*?</section>\s*',
    re.DOTALL | re.IGNORECASE,
)
SERVICE_LINKS_SECTION_RE = re.compile(
    r'<section\b[^>]*\bid="service-links"[^>]*>.*?</section>\s*',
    re.DOTALL | re.IGNORECASE,
)
FAQ_SECTION_RE = re.compile(r'<section\b[^>]*\bid="faq"[^>]*>', re.IGNORECASE)
REVIEWS_SECTION_RE = re.compile(r'<section\b[^>]*\bid="reviews-embed"[^>]*>', re.IGNORECASE)
FOOTER_RE = re.compile(r'<footer\b', re.IGNORECASE)
ANCHOR_RE = re.compile(
    r'<a\b([^>]*?)\bclass="([^"]*)"([^>]*?)\bhref="([^"]+)"([^>]*?)>',
    re.IGNORECASE,
)
TITLE_RE = re.compile(r'<title>\s*([^<]+?)\s*</title>', re.I)
H1_RE = re.compile(r'<h1[^>]*>\s*([^<]+?)\s*</h1>', re.I)


def html_escape(s: str) -> str:
    return (s.replace('&', '&amp;').replace('<', '&lt;')
             .replace('>', '&gt;').replace('"', '&quot;'))


def html_unescape(s: str) -> str:
    return (s.replace('&amp;', '&').replace('&quot;', '"')
             .replace('&#39;', "'").replace('&lt;', '<').replace('&gt;', '>'))


def read_html(p: Path) -> str:
    return p.read_text(encoding='utf-8', errors='replace')


def extract_title(html: str) -> str:
    m = H1_RE.search(html)
    if m:
        return html_unescape(m.group(1).strip())
    m = TITLE_RE.search(html)
    if m:
        return html_unescape(m.group(1).strip())
    return 'Untitled'


def classify_dir(dirname: str) -> tuple[str | None, str | None, str | None]:
    """Return (kind, service_hub_dir, city_slug) for a top-level dir.
    kind in {'hub','location','blog',None}"""
    if dirname in HUB_DIRS:
        return ('hub', dirname, None)

    # Try every service's location patterns.
    for svc in SERVICES:
        for pat in svc['location_patterns']:
            m = re.match(pat, dirname)
            if not m:
                continue
            city = m.group('city')
            if city in CITIES:
                return ('location', svc['hub_dir'], city)
    return (None, None, None)


def classify_blog(dirname: str, html: str) -> tuple[str | None, str | None]:
    """Return (service_hub_dir, city_slug) for a blog dir.
    Uses slug + content keywords; city is matched against known CITIES."""
    if dirname in DUPLICATE_HUB_SLUGS:
        return (None, None)

    title = extract_title(html)[:200]
    cat_match = re.search(r'<span\s+class="category"[^>]*>(.*?)</span>', html, re.I | re.S)
    category = cat_match.group(1).strip() if cat_match else ''
    text = (dirname + ' ' + title + ' ' + category).lower()
    matched_svc: str | None = None

    # First pass: pick the FIRST matching service (order in SERVICES = priority).
    for svc in SERVICES:
        if any(ex in text for ex in svc['blog_excludes']):
            # Negative match — skip this service
            continue
        if any(kw in text for kw in svc['blog_keywords']):
            matched_svc = svc['hub_dir']
            break

    if not matched_svc:
        return (None, None)

    # Detect city from slug. Longest match wins (so 'east-york' before 'york').
    city = None
    for slug in sorted(CITIES.keys(), key=len, reverse=True):
        if re.search(r'(?:^|-)' + re.escape(slug) + r'(?:-|$)', dirname):
            city = slug
            break
    return (matched_svc, city)


# Section builders --------------------------------------------------------

def build_locations_section(label: str, location_pairs: list[tuple[str, str]]) -> str:
    cards = '\n'.join(
        f'<a class="location-card" href="{u}">{html_escape(name)}</a>'
        for (u, name) in location_pairs
    )
    return (
        f'<section aria-label="Service locations" class="island reveal service-locations" id="locations">\n'
        f'<span aria-hidden="true" class="shine"></span>\n'
        f'<div class="section-head">\n'
        f'<h2>{html_escape(label)} Services in Your Area</h2>\n'
        f'<p>We provide {html_escape(label.lower())} services across the Greater Toronto Area. Select your location:</p>\n'
        f'</div>\n'
        f'<div class="location-grid">\n'
        f'{cards}\n'
        f'</div>\n'
        f'</section>'
    )


def build_related_articles_section(label: str, blog_pairs: list[tuple[str, str]]) -> str:
    if not blog_pairs:
        return ''
    cards = '\n'.join(
        f'<a class="card" href="{u}"><h3>{html_escape(t)}</h3></a>'
        for (u, t) in blog_pairs
    )
    return (
        f'<section aria-label="Related articles" class="island reveal" id="related-articles">\n'
        f'<span aria-hidden="true" class="shine"></span>\n'
        f'<div class="section-head">\n'
        f'<h2>{html_escape(label)} Guides &amp; Articles</h2>\n'
        f'<p>Tips and guides on {html_escape(label.lower())} from our team.</p>\n'
        f'</div>\n'
        f'<div class="cards related-cards">\n'
        f'{cards}\n'
        f'</div>\n'
        f'</section>'
    )


def build_related_blogs_section(blog_pairs: list[tuple[str, str]]) -> str:
    if not blog_pairs:
        return ''
    cards = '\n'.join(
        f'<a class="card" href="{u}"><h3>{html_escape(t)}</h3></a>'
        for (u, t) in blog_pairs
    )
    return (
        f'<section aria-label="Related articles" class="island reveal" id="related-blogs">\n'
        f'<span aria-hidden="true" class="shine"></span>\n'
        f'<div class="section-head">\n'
        f'<h2>Related Articles</h2>\n'
        f'</div>\n'
        f'<div class="cards related-cards">\n'
        f'{cards}\n'
        f'</div>\n'
        f'</section>'
    )


def build_service_links_section(service_label: str, hub_url: str,
                                 city_label: str | None,
                                 city_url: str | None) -> str:
    rows = [f'<li><a href="{hub_url}">{html_escape(service_label)} — main service page</a></li>']
    if city_label and city_url:
        rows.append(f'<li><a href="{city_url}">{html_escape(service_label)} in {html_escape(city_label)}</a></li>')
    return (
        f'<section aria-label="Related service" class="island reveal" id="service-links">\n'
        f'<span aria-hidden="true" class="shine"></span>\n'
        f'<div class="section-head">\n'
        f'<h2>Related Service</h2>\n'
        f'</div>\n'
        f'<ul class="service-links-list" style="padding:0 24px 16px;list-style:disc;margin:0 0 0 18px;">\n'
        + '\n'.join(rows) + '\n'
        f'</ul>\n'
        f'</section>'
    )


def upsert_section(html: str, section_html: str, marker_re: re.Pattern,
                   anchor_re: re.Pattern) -> str:
    """Replace section if present; else insert before anchor (or footer)."""
    if not section_html:
        return marker_re.sub('', html)
    if marker_re.search(html):
        return marker_re.sub(section_html + '\n', html, count=1)
    m = anchor_re.search(html)
    if m:
        return html[:m.start()] + section_html + '\n' + html[m.start():]
    m = FOOTER_RE.search(html)
    if m:
        return html[:m.start()] + section_html + '\n' + html[m.start():]
    return html + '\n' + section_html


def fix_cta_to_book(html: str, location_urls: set[str], book_url: str
                    ) -> tuple[str, list[tuple[str, str]]]:
    findings: list[tuple[str, str]] = []

    def _replace(m: re.Match) -> str:
        attrs1, classes, attrs2, href, attrs3 = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        if 'btn' not in classes.split():
            return m.group(0)
        if href in location_urls:
            findings.append((href, classes))
            return f'<a{attrs1}class="{classes}"{attrs2} href="{book_url}"{attrs3}>'
        return m.group(0)

    return ANCHOR_RE.sub(_replace, html), findings


# Main --------------------------------------------------------------------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--max-related', type=int, default=8)
    ap.add_argument('--only', help='Restrict to one hub dir (for testing)')
    ap.add_argument('--list-blogs', action='store_true',
                    help='Print the full list of blog candidates with hub/city and exit.')
    args = ap.parse_args(argv)
    apply = bool(args.apply)

    # 1) Discover all top-level dirs and classify them.
    locations: dict[str, list[tuple[str, str, str]]] = {s['hub_dir']: [] for s in SERVICES}
    # locations[hub_dir] = list of (url, city_slug, city_name)
    blog_classifications: list[tuple[str, str, str | None]] = []
    # (rel_path, hub_dir, city_slug or None) where rel_path uses '/' separator
    unclassified: list[str] = []

    candidate_dirs: list[Path] = []
    for d in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        name = d.name
        if name.startswith('.') or name in SKIP_DIRS:
            continue
        if name == 'blog':
            continue  # listing page, not a service blog post
        if (d / 'index.html').exists():
            candidate_dirs.append(d)

    # Also walk one level into /blog/ which is otherwise skipped.
    blog_root = ROOT / 'blog'
    if blog_root.is_dir():
        for d in sorted(p for p in blog_root.iterdir() if p.is_dir()):
            if d.name.startswith('.'):
                continue
            if (d / 'index.html').exists():
                candidate_dirs.append(d)

    for d in candidate_dirs:
        rel = d.relative_to(ROOT).as_posix()
        index = d / 'index.html'

        # Top-level dir uses just the name; nested (blog/x) uses full rel path.
        if '/' in rel:
            # Nested -> always classify as blog
            try:
                html = read_html(index)
            except Exception:
                unclassified.append(rel)
                continue
            blog_hub, blog_city = classify_blog(rel.replace('/', '-'), html)
            if blog_hub:
                blog_classifications.append((rel, blog_hub, blog_city))
            else:
                unclassified.append(rel)
            continue

        name = rel
        if name in DUPLICATE_HUB_SLUGS:
            # Leave the page on disk; just skip cross-linking.
            unclassified.append(name + ' (duplicate-hub, ignored)')
            continue

        kind, hub_dir, city = classify_dir(name)
        if kind == 'hub':
            continue
        if kind == 'location':
            assert hub_dir and city
            locations[hub_dir].append((f'/{name}/', city, CITIES[city]))
            continue

        try:
            html = read_html(index)
        except Exception:
            unclassified.append(name)
            continue
        blog_hub, blog_city = classify_blog(name, html)
        if blog_hub:
            blog_classifications.append((name, blog_hub, blog_city))
        else:
            unclassified.append(name)

    # 2) Build maps for blog->hub and (hub,city)->blog
    blogs_by_hub: dict[str, list[tuple[str, str]]] = {s['hub_dir']: [] for s in SERVICES}
    blogs_general_by_hub: dict[str, list[tuple[str, str]]] = {s['hub_dir']: [] for s in SERVICES}
    blogs_by_hub_city: dict[tuple[str, str], list[tuple[str, str]]] = {}
    blog_hub_city_map: dict[str, tuple[str, str | None]] = {}
    blog_titles: dict[str, str] = {}

    for rel, hub, city in blog_classifications:
        url = f'/{rel}/'
        try:
            title = extract_title(read_html(ROOT / rel / 'index.html'))
        except Exception:
            title = rel.replace('-', ' ').replace('/', ' / ').title()
        blog_titles[rel] = title
        blog_hub_city_map[rel] = (hub, city)
        blogs_by_hub[hub].append((url, title))
        if city is None:
            blogs_general_by_hub[hub].append((url, title))
        else:
            blogs_by_hub_city.setdefault((hub, city), []).append((url, title))

    if args.list_blogs:
        print(f'{"REL":<70} {"HUB":<42} {"CITY":<20} TITLE')
        print('-' * 200)
        for rel in sorted(blog_hub_city_map):
            hub, city = blog_hub_city_map[rel]
            print(f'{rel:<70} {hub:<42} {(city or "-"):<20} {blog_titles.get(rel, "")[:80]}')
        print(f'\nTotal blog candidates: {len(blog_hub_city_map)}')
        return 0

    # 3) Build set of all known location URLs (for CTA detection).
    all_location_urls: set[str] = {
        url
        for arr in locations.values()
        for (url, _c, _n) in arr
    }

    # 4) Process each hub.
    print('=' * 100)
    print(f'RESTRUCTURE HUBS  (apply={apply})  only={args.only or "<all>"}')
    print('=' * 100)

    fixed_count = 0
    issue_count = 0
    skipped_blog_dirs: list[str] = unclassified.copy()

    for svc in SERVICES:
        if args.only and svc['hub_dir'] != args.only:
            continue

        hub_dir = svc['hub_dir']
        label = svc['label']
        book_url = svc['book_url']
        hub_file = ROOT / hub_dir / 'index.html'
        if not hub_file.exists():
            print(f'\n[!] HUB MISSING: /{hub_dir}/')
            continue

        loc_pairs_raw = sorted(set((u, slug, name) for (u, slug, name) in locations[hub_dir]))
        loc_pairs = [(u, name) for (u, _slug, name) in
                     sorted(loc_pairs_raw, key=lambda t: t[2].lower())]
        general_blog_pairs = blogs_general_by_hub[hub_dir][:args.max_related]

        html = read_html(hub_file)
        original_html = html

        print(f'\n--- /{hub_dir}/   "{label}"')

        # CTA fix
        new_html, cta_findings = fix_cta_to_book(html, all_location_urls, book_url)
        if cta_findings:
            issue_count += len(cta_findings)
            for href, classes in cta_findings:
                print(f'  [CTA]   wrong button -> {href}  =>  {book_url}  (classes="{classes}")')
            html = new_html
        else:
            print('  [CTA]   ok')

        # Locations grid
        existing_loc_links: set[str] = set()
        m_loc = LOCATIONS_SECTION_RE.search(html)
        if m_loc:
            existing_loc_links = set(re.findall(r'href="(/[^"#]+/)"', m_loc.group(0)))
        expected_urls = {u for (u, _n) in loc_pairs}
        missing_urls = expected_urls - existing_loc_links
        extra_urls = existing_loc_links - expected_urls

        if loc_pairs:
            print(f'  [LOC]   total={len(expected_urls)}  present={len(existing_loc_links & expected_urls)}  add={len(missing_urls)}  remove={len(extra_urls)}')
            for u in sorted(missing_urls):
                issue_count += 1
                print(f'          + {u}')
            for u in sorted(extra_urls):
                print(f'          - {u} (drop, not classified for this service)')
            new_section = build_locations_section(label, loc_pairs)
            html = upsert_section(html, new_section, LOCATIONS_SECTION_RE, FAQ_SECTION_RE)
        else:
            print('  [LOC]   no locations classified for this service')

        # Related Articles (general blogs only)
        existing_rel: set[str] = set()
        m_rel = RELATED_ARTICLES_SECTION_RE.search(html)
        if m_rel:
            existing_rel = set(re.findall(r'href="(/[^"#]+/)"', m_rel.group(0)))
        expected_blog_urls = {u for (u, _t) in general_blog_pairs}
        missing_blog_urls = expected_blog_urls - existing_rel

        if general_blog_pairs:
            print(f'  [BLOG]  general={len(expected_blog_urls)}  present={len(existing_rel & expected_blog_urls)}  add={len(missing_blog_urls)}')
            for u in sorted(missing_blog_urls):
                issue_count += 1
                print(f'          + {u}')
            new_block = build_related_articles_section(label, general_blog_pairs)
            html = upsert_section(html, new_block, RELATED_ARTICLES_SECTION_RE, FAQ_SECTION_RE)
        else:
            print('  [BLOG]  no general (non-location) blogs classified for this service')
            if RELATED_ARTICLES_SECTION_RE.search(html):
                html = RELATED_ARTICLES_SECTION_RE.sub('', html)
                print('          - removing stale related-articles section')

        if html != original_html:
            fixed_count += 1
            if apply:
                hub_file.write_bytes(html.encode('utf-8'))
                print('  [WRITE] applied')
            else:
                print('  [DRY]   would change')

    # 5) Process each location page (related-blogs section)
    if not args.only:
        print('\n' + '-' * 100)
        print('LOCATION PAGES — related-blogs')
        print('-' * 100)
        loc_changed = 0
        for svc in SERVICES:
            hub_dir = svc['hub_dir']
            label = svc['label']
            for (loc_url, city_slug, city_name) in sorted(locations[hub_dir],
                                                          key=lambda t: t[2].lower()):
                page = ROOT / loc_url.strip('/') / 'index.html'
                if not page.exists():
                    continue
                html = read_html(page)
                original = html

                # Pick city-specific blogs first; fall back to general.
                items = list(blogs_by_hub_city.get((hub_dir, city_slug), []))
                if len(items) < args.max_related:
                    seen = {u for (u, _t) in items}
                    for (u, t) in blogs_general_by_hub[hub_dir]:
                        if u in seen:
                            continue
                        items.append((u, t))
                        if len(items) >= args.max_related:
                            break

                section = build_related_blogs_section(items[:args.max_related])
                html = upsert_section(html, section, RELATED_BLOGS_SECTION_RE, FAQ_SECTION_RE)

                # Also ensure CTA buttons on this location page point to its book form.
                # Buttons that go to OTHER location pages should NOT happen on a location page,
                # but we leave links pointing to its OWN city alone.
                # Skipping this to stay surgical.

                if html != original:
                    loc_changed += 1
                    if apply:
                        page.write_bytes(html.encode('utf-8'))
        print(f'Location pages updated: {loc_changed}')

    # 6) Process each blog page (service-links section)
    if not args.only:
        print('\n' + '-' * 100)
        print('BLOG PAGES — service-links')
        print('-' * 100)
        blog_changed = 0
        for rel, (hub_dir, city_slug) in blog_hub_city_map.items():
            page = ROOT / rel / 'index.html'
            if not page.exists():
                continue
            svc = next((s for s in SERVICES if s['hub_dir'] == hub_dir), None)
            if not svc:
                continue
            html = read_html(page)
            original = html
            hub_url = f'/{hub_dir}/'

            city_label = None
            city_url = None
            if city_slug:
                # Find a location page of this hub for this city.
                for (u, slug, cname) in locations[hub_dir]:
                    if slug == city_slug:
                        city_label = cname
                        city_url = u
                        break
                if not city_label:
                    city_label = CITIES.get(city_slug)

            section = build_service_links_section(svc['label'], hub_url, city_label, city_url)
            html = upsert_section(html, section, SERVICE_LINKS_SECTION_RE, FAQ_SECTION_RE)
            if html != original:
                blog_changed += 1
                if apply:
                    page.write_bytes(html.encode('utf-8'))
        print(f'Blog pages updated: {blog_changed}')

    # Summary
    print('\n' + '=' * 100)
    print(f'Hubs touched: {fixed_count} / {len(SERVICES)}')
    print(f'Total hub issues found: {issue_count}')
    if skipped_blog_dirs:
        print(f'Unclassified top-level dirs (kept untouched): {len(skipped_blog_dirs)}')
        for n in sorted(skipped_blog_dirs)[:30]:
            print(f'  ? {n}')
        if len(skipped_blog_dirs) > 30:
            print(f'  ... and {len(skipped_blog_dirs)-30} more')
    print('=' * 100)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
