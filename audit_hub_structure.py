"""audit_hub_structure.py

Audit + fix Hub <-> Location <-> Blog structure across all 18 service hubs.

Rules (per user):
  - 1 Hub per service (non-location). Existing pages only — NEVER create new ones.
  - Hub primary CTA must point to /book-*.html, never to a location page.
  - Hub `#locations` grid must include EVERY existing service+location page of that service.
  - Hub `#related-articles` must list ONLY non-location blogs of that service.
  - Location-specific blogs are the responsibility of location pages
    (handled by link_blogs_services_locations.py).

Usage:
  python audit_hub_structure.py            # dry-run report
  python audit_hub_structure.py --apply    # apply fixes
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Reuse the existing classifier infrastructure.
import link_blogs_services_locations as lbs  # noqa: E402

ROOT = Path(__file__).parent.resolve()

# Inline locations table — bypass broken import in generate_service_pages.py.
# Covers all known city slugs used across the site.
_LOCATIONS_INLINE: list[tuple[str, str]] = [
    ('Toronto', 'toronto'),
    ('North York', 'north-york'),
    ('East York', 'east-york'),
    ('Scarborough', 'scarborough'),
    ('Etobicoke', 'etobicoke'),
    ('Markham', 'markham'),
    ('Richmond Hill', 'richmond-hill'),
    ('Vaughan', 'vaughan'),
    ('Woodbridge', 'woodbridge'),
    ('Aurora', 'aurora'),
    ('Newmarket', 'newmarket'),
    ('Thornhill', 'thornhill'),
    ('King City', 'king-city'),
    ('Kleinburg', 'kleinburg'),
    ('Concord', 'concord'),
    ('Maple', 'maple'),
    ('Mississauga', 'mississauga'),
    ('Oakville', 'oakville'),
    ('Burlington', 'burlington'),
    ('Hamilton', 'hamilton'),
    ('Brampton', 'brampton'),
    ('Bradford', 'bradford'),
    ('East Gwillimbury', 'east-gwillimbury'),
    ('Schomberg', 'schomberg'),
    ('Forest Hill', 'forest-hill'),
    ('Bayview Glen', 'bayview-glen'),
    ('Glenville', 'glenville'),
    ('Whitchurch-Stouffville', 'whitchurch'),
]


def _patched_load_locations() -> list[lbs.Location]:
    return [lbs.Location(name=n, slug=s) for (n, s) in _LOCATIONS_INLINE]


# Replace the broken loader BEFORE any code calls it.
lbs.load_locations = _patched_load_locations  # type: ignore[assignment]

# 18 service hubs: hub_dir -> (service_id matching link_blogs classifier, label, book_url)
HUBS: dict[str, tuple[str, str, str]] = {
    'deck-builder':                              ('deck-building',     'Deck Building',     '/book-deck.html'),
    'deck-railings':                             ('deck-railings',     'Deck Railings',     '/book-railing.html'),
    'fence-contractor-in-toronto':               ('fence-installation','Fence Installation','/book-fence.html'),
    'bathroom-renovation':                       ('bathroom-renovation','Bathroom Renovation','/book-bathroom.html'),
    'basement-renovation-service-in-toronto':    ('basement-renovation','Basement Renovation','/book-basement.html'),
    'handyman-plumbing-services':                ('plumbing',          'Plumbing',          '/book-plumbing.html'),
    'canopy':                                    ('canopy-awnings',    'Canopy & Awnings',  '/book-canopy.html'),
    'landscaping-services-toronto':              ('landscaping',       'Landscaping',       '/book-landscaping.html'),
    'general-contractor-in-toronto':             ('general-contractor','General Contractor','/book-contractor.html'),
    'handyman-service-in-toronto':               ('handyman',          'Handyman',          '/book-handy.html'),
    'interlocking-paver-services':               ('interlocking-paving','Interlocking',     '/book-interlock.html'),
    'carpenter-services':                        ('carpentry',         'Carpentry',         '/book-carpentry.html'),
    'electrical-handyman-services':              ('electrical',        'Electrical',        '/book-electrical.html'),
    'handyman-painting-services':                ('painting',          'Painting',          '/book-painting.html'),
    'demolition-services':                       ('demolition',        'Demolition',        '/book-demolition.html'),
    'excavation-services':                       ('excavation',        'Excavation',        '/book-excavation.html'),
    'home-renovation':                           ('home-renovation',   'Home Renovation',   '/book-renovation.html'),
    'christmas-lights-installation-toronto-gta': ('christmas-lights',  'Christmas Lights',  '/book-christmas.html'),
}

# Hub dirs are NOT locations even if their slug looks location-ish.
HUB_DIRS: set[str] = set(HUBS.keys())

# Sections we manage on the hub.
LOCATIONS_SECTION_RE = re.compile(
    r'<section\b[^>]*id="locations"[^>]*>.*?</section>\s*',
    re.DOTALL | re.IGNORECASE,
)
RELATED_ARTICLES_SECTION_RE = re.compile(
    r'<section\b[^>]*id="related-articles"[^>]*>.*?</section>\s*',
    re.DOTALL | re.IGNORECASE,
)
FAQ_SECTION_RE = re.compile(
    r'<section\b[^>]*id="faq"[^>]*>',
    re.IGNORECASE,
)
FOOTER_RE = re.compile(r'<footer\b', re.IGNORECASE)

# CTA buttons on the hub. We treat any <a class="...btn..."> as a CTA.
ANCHOR_RE = re.compile(
    r'<a\b([^>]*?)\bclass="([^"]*)"([^>]*)\bhref="([^"]+)"([^>]*)>',
    re.IGNORECASE,
)


def html_escape(s: str) -> str:
    return (s.replace('&', '&amp;').replace('<', '&lt;')
             .replace('>', '&gt;').replace('"', '&quot;'))


def pretty_city_from_slug(loc_slug: str) -> str:
    # Try the LOCATIONS table first; otherwise titlecase the slug.
    locs = lbs.load_locations()
    for loc in locs:
        if loc.slug == loc_slug:
            return loc.name
    return loc_slug.replace('-', ' ').title()


def build_locations_section(label: str, location_pairs: list[tuple[str, str]]) -> str:
    """location_pairs: [(url, City)]"""
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
    """blog_pairs: [(url, Title)]"""
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


def upsert_section(html: str, section_html: str, marker_re: re.Pattern,
                   anchor_for_insert_re: re.Pattern) -> str:
    """Replace section if already present (matched by marker_re); otherwise
    insert the block right before the anchor element matched by anchor_for_insert_re."""
    if not section_html:
        # Caller asked for empty (no related articles to render). Strip if exists.
        return marker_re.sub('', html)
    if marker_re.search(html):
        return marker_re.sub(section_html + '\n', html, count=1)
    m = anchor_for_insert_re.search(html)
    if m:
        return html[:m.start()] + section_html + '\n' + html[m.start():]
    # Fallback: before <footer>
    m = FOOTER_RE.search(html)
    if m:
        return html[:m.start()] + section_html + '\n' + html[m.start():]
    return html + '\n' + section_html


def fix_cta_to_book(html: str, location_urls: set[str], book_url: str
                    ) -> tuple[str, list[tuple[str, str]]]:
    """Replace any <a class="...btn..." href="/some-location/"> with book_url.
    Returns (new_html, list_of_(old_href, button_text))."""
    # Quick path: if no candidate location URL appears as href, return unchanged.
    findings: list[tuple[str, str]] = []

    def _replace(m: re.Match) -> str:
        attrs1, classes, attrs2, href, attrs3 = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        if 'btn' not in classes.split():
            return m.group(0)
        if href in location_urls:
            findings.append((href, classes))
            new_attrs = f'{attrs1}class="{classes}"{attrs2} href="{book_url}"{attrs3}'
            return f'<a{new_attrs}>'
        return m.group(0)

    new_html = ANCHOR_RE.sub(_replace, html)
    return new_html, findings


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--max-related', type=int, default=8)
    args = ap.parse_args(argv)

    apply = bool(args.apply)
    locations = lbs.load_locations()
    blogs, service_pages = lbs.discover_pages(ROOT, locations)

    # Build maps
    locs_by_service: dict[str, list[lbs.ServicePage]] = {}
    for sp in service_pages:
        if not sp.service_id or not sp.location_slug:
            continue
        if sp.rel_dir in HUB_DIRS:
            continue  # The hub itself is not a "location"
        locs_by_service.setdefault(sp.service_id, []).append(sp)

    blogs_by_service: dict[str, list[lbs.BlogPost]] = {}
    blogs_by_service_general: dict[str, list[lbs.BlogPost]] = {}
    for bp in blogs:
        if not bp.service_id:
            continue
        blogs_by_service.setdefault(bp.service_id, []).append(bp)
        if not bp.location_slug:
            blogs_by_service_general.setdefault(bp.service_id, []).append(bp)

    # All location URLs across ALL services (for CTA detection).
    all_location_urls: set[str] = {
        sp.url for sp in service_pages
        if sp.location_slug and sp.rel_dir not in HUB_DIRS
    }

    print('=' * 88)
    print(f'HUB STRUCTURE AUDIT  (apply={apply})')
    print('=' * 88)

    fixed_count = 0
    issue_count = 0

    for hub_dir, (service_id, label, book_url) in HUBS.items():
        hub_file = ROOT / hub_dir / 'index.html'
        if not hub_file.exists():
            print(f'\n[!] HUB MISSING ON DISK: /{hub_dir}/')
            continue

        html = hub_file.read_text(encoding='utf-8', errors='replace')
        original_html = html

        loc_pages = locs_by_service.get(service_id, [])
        loc_pairs: list[tuple[str, str]] = []
        for sp in sorted(loc_pages, key=lambda x: x.location_slug or ''):
            city = pretty_city_from_slug(sp.location_slug or '')
            loc_pairs.append((sp.url, city))

        general_blogs = blogs_by_service_general.get(service_id, [])
        general_blog_pairs = [(bp.url, bp.title) for bp in general_blogs[:args.max_related]]

        print(f'\n--- /{hub_dir}/  service_id={service_id}  label="{label}"')

        # 1) CTA fix
        new_html, cta_findings = fix_cta_to_book(html, all_location_urls, book_url)
        if cta_findings:
            issue_count += len(cta_findings)
            for href, classes in cta_findings:
                print(f'  [CTA]   wrong button -> {href}   (classes="{classes}")  =>  {book_url}')
            html = new_html
        else:
            print('  [CTA]   ok (no CTA buttons point to a location)')

        # 2) Locations grid: ensure ALL existing locations are linked.
        existing_loc_links: set[str] = set()
        m_loc = LOCATIONS_SECTION_RE.search(html)
        if m_loc:
            existing_loc_links = set(re.findall(r'href="(/[^"]+/)"', m_loc.group(0)))
        expected_urls = {u for (u, _n) in loc_pairs}
        missing_urls = expected_urls - existing_loc_links
        extra_urls = existing_loc_links - expected_urls

        if loc_pairs:
            print(f'  [LOC]   {len(expected_urls)} expected, {len(existing_loc_links & expected_urls)} present, {len(missing_urls)} missing')
            if missing_urls:
                for u in sorted(missing_urls):
                    issue_count += 1
                    print(f'          + add  {u}')
            if extra_urls:
                # Not all extras are bad, but flag for review.
                for u in sorted(extra_urls):
                    print(f'          ? extra (not in classifier set, will be removed on rebuild): {u}')
            new_section = build_locations_section(label, loc_pairs)
            html = upsert_section(html, new_section, LOCATIONS_SECTION_RE, FAQ_SECTION_RE)
        else:
            print('  [LOC]   no location pages classified for this service (skipping)')

        # 3) Related Articles: only non-location blogs.
        existing_related_links: set[str] = set()
        m_rel = RELATED_ARTICLES_SECTION_RE.search(html)
        if m_rel:
            existing_related_links = set(re.findall(r'href="(/[^"]+/)"', m_rel.group(0)))
        expected_blog_urls = {u for (u, _t) in general_blog_pairs}
        missing_blog_urls = expected_blog_urls - existing_related_links

        if general_blog_pairs:
            print(f'  [BLOG]  {len(expected_blog_urls)} general blogs available, {len(existing_related_links & expected_blog_urls)} present, {len(missing_blog_urls)} missing')
            for u in sorted(missing_blog_urls):
                issue_count += 1
                print(f'          + add  {u}')
            new_block = build_related_articles_section(label, general_blog_pairs)
            html = upsert_section(html, new_block, RELATED_ARTICLES_SECTION_RE, FAQ_SECTION_RE)
        else:
            print('  [BLOG]  no general (non-location) blogs available for this service')
            # Strip the section if it exists with stale content.
            if RELATED_ARTICLES_SECTION_RE.search(html):
                html = RELATED_ARTICLES_SECTION_RE.sub('', html)
                print('          - removing stale related-articles section')

        if html != original_html:
            if apply:
                hub_file.write_bytes(html.encode('utf-8'))
                fixed_count += 1
                print('  [WRITE] applied changes')
            else:
                fixed_count += 1
                print('  [DRY]   would change file (run with --apply)')

    print('\n' + '=' * 88)
    print(f'Hubs touched: {fixed_count} / {len(HUBS)}')
    print(f'Total issues found: {issue_count}')
    print('=' * 88)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
