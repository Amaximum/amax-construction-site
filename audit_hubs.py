"""Audit all 18 service hub pages for SEO and design issues."""
from pathlib import Path
import re

HUBS = {
    'deck-builder': ('Deck Building', '/book-deck.html'),
    'deck-railings': ('Deck Railings', '/book-railing.html'),
    'fence-contractor-in-toronto': ('Fence Installation', '/book-fence.html'),
    'bathroom-renovation': ('Bathroom Renovation', '/book-bathroom.html'),
    'basement-renovation-service-in-toronto': ('Basement Renovation', '/book-basement.html'),
    'handyman-plumbing-services': ('Plumbing', '/book-plumbing.html'),
    'canopy': ('Canopy & Awnings', '/book-canopy.html'),
    'landscaping-services-toronto': ('Landscaping', '/book-landscaping.html'),
    'general-contractor-in-toronto': ('General Contractor', '/book-contractor.html'),
    'handyman-service-in-toronto': ('Handyman', '/book-handy.html'),
    'interlocking-paver-services': ('Interlocking', '/book-interlock.html'),
    'carpenter-services': ('Carpentry', '/book-carpentry.html'),
    'electrical-handyman-services': ('Electrical', '/book-electrical.html'),
    'handyman-painting-services': ('Painting', '/book-painting.html'),
    'demolition-services': ('Demolition', '/book-demolition.html'),
    'excavation-services': ('Excavation', '/book-excavation.html'),
    'home-renovation': ('Home Renovation', '/book-renovation.html'),
    'christmas-lights-installation-toronto-gta': ('Christmas Lights', '/book-christmas.html'),
}

root = Path('.')

print(f"{'PAGE':<45} {'TITLE_LEN':>9} {'DESC_LEN':>8} {'H1':>3} {'SCHEMA':>8} {'ISLAND':>6} {'BOOK_OK':>7} {'OG':>3}")
print('-' * 110)

for slug, (label, book_url) in HUBS.items():
    idx = root / slug / 'index.html'
    if not idx.exists():
        print(f'{slug:<45} NOT FOUND')
        continue
    html = idx.read_text(encoding='utf-8', errors='ignore')

    # Title
    m = re.search(r'<title>([^<]+)</title>', html, re.I)
    title_len = len(m.group(1)) if m else 0

    # Meta description
    m = re.search(r'<meta name="description" content="([^"]*)"', html, re.I)
    desc_len = len(m.group(1)) if m else 0

    # H1 count
    h1_count = len(re.findall(r'<h1', html, re.I))

    # Schema type
    schema_types = re.findall(r'"@type"\s*:\s*"([^"]+)"', html)
    schema = ','.join(set(schema_types) - {'Organization', 'ImageObject', 'ListItem', 'BreadcrumbList'}) or 'NONE'

    # Uses island/cards design
    has_island = 'class="island' in html
    has_cards = 'class="cards"' in html or 'class="card"' in html

    # BOOK NOW points to correct URL
    book_ok = book_url in html

    # OG tags
    has_og = 'og:title' in html and 'og:description' in html

    # Old container structure
    has_old = 'class="container"' in html or 'class="content"' in html

    flags = []
    if title_len < 30 or title_len > 65: flags.append(f'TITLE:{title_len}')
    if desc_len < 120 or desc_len > 160: flags.append(f'DESC:{desc_len}')
    if h1_count != 1: flags.append(f'H1:{h1_count}')
    if 'Service' not in schema and 'LocalBusiness' not in schema: flags.append(f'SCHEMA:{schema}')
    if not has_island: flags.append('NO_ISLAND')
    if not book_ok: flags.append('WRONG_BOOK')
    if not has_og: flags.append('NO_OG')
    if has_old: flags.append('OLD_LAYOUT')

    status = ' | '.join(flags) if flags else 'OK'
    print(f'{slug:<45} {title_len:>9} {desc_len:>8} {h1_count:>3} {schema[:10]:>10} {"Y" if has_island else "N":>6} {"Y" if book_ok else "N":>7} {"Y" if has_og else "N":>3}  {status}')
