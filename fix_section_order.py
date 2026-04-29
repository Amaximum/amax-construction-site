"""
Fix duplicate sections and set correct section order on all 18 service hub pages.

Correct order:
 1. <nav> / header
 2. page-hero
 3. Why Choose Us
 4. Service Types (what we offer)
 5. How It Works (process)
 6. Reviews embed
 7. Service Locations
 8. Related Articles (blogs)
 9. Mid-page CTA (orange)
10. Our Other Services
11. FAQ  ← very last before footer
12. <footer>
"""
import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

SLUGS = [
    'deck-builder', 'deck-railings', 'fence-contractor-in-toronto',
    'bathroom-renovation', 'basement-renovation-service-in-toronto',
    'handyman-plumbing-services', 'canopy', 'landscaping-services-toronto',
    'general-contractor-in-toronto', 'handyman-service-in-toronto',
    'interlocking-paver-services', 'carpenter-services',
    'electrical-handyman-services', 'handyman-painting-services',
    'demolition-services', 'excavation-services',
    'home-renovation', 'christmas-lights-installation-toronto-gta',
]

root = Path('.')

def classify_section(tag):
    """Return a string key for each section type."""
    sid = tag.get('id', '')
    label = tag.get('aria-label', '').lower()
    cls = ' '.join(tag.get('class', []))

    if sid == 'reviews-embed':
        return 'reviews'
    if sid == 'faq':
        return 'faq'
    if sid == 'how-it-works':
        return 'process'
    if sid == 'service-types':
        return 'service_types'
    if sid in ('locations', 'service-areas'):
        return 'locations'
    if sid == 'articles':
        return 'articles'
    if 'why choose' in label or 'why-choose' in sid:
        return 'why_choose'
    if 'other service' in label:
        return 'other_services'
    if 'call to action' in label or (
        tag.get('style', '') and 'ff6b00' in tag.get('style', '')
    ):
        return 'cta'
    if 'related-articles' in cls or 'related article' in label:
        return 'articles'
    if 'service-locations' in cls or 'service location' in label:
        return 'locations'
    return 'unknown'

# Desired order of section keys
ORDER = [
    'why_choose',
    'service_types',
    'process',
    'reviews',
    'locations',
    'articles',
    'cta',
    'other_services',
    'faq',
]

updated = []

for slug in SLUGS:
    idx = root / slug / 'index.html'
    if not idx.exists():
        print(f'  SKIP: {slug}')
        continue

    html = idx.read_text(encoding='utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')

    body = soup.body
    if not body:
        print(f'  SKIP (no body): {slug}')
        continue

    # Collect all <section> tags and the footer
    sections = body.find_all('section', recursive=False)

    # Also check inside wrappers
    if not sections:
        sections = body.find_all('section')

    # Build a dict: key -> first section tag of that type
    seen_keys = {}
    duplicate_sections = []

    for sec in sections:
        key = classify_section(sec)
        if key not in seen_keys:
            seen_keys[key] = sec
        else:
            # Mark duplicates for removal
            duplicate_sections.append(sec)

    # Remove duplicates from DOM
    for dup in duplicate_sections:
        dup.decompose()

    # Find footer and page-hero
    footer = body.find('footer')
    hero = body.find(class_=re.compile(r'page-hero'))

    # Remove all sections from body temporarily, we'll re-insert in order
    for sec in list(body.find_all('section')):
        sec.extract()

    # Remove footer temporarily
    if footer:
        footer.extract()

    # Re-insert sections in correct order after the hero
    insert_after = hero if hero else body

    for key in ORDER:
        sec = seen_keys.get(key)
        if sec:
            body.append(sec)

    # Append any unknown sections
    for key, sec in seen_keys.items():
        if key not in ORDER and key != 'unknown':
            body.append(sec)
    for key, sec in seen_keys.items():
        if key == 'unknown':
            body.append(sec)

    # Re-append footer last
    if footer:
        body.append(footer)

    result = str(soup)
    idx.write_text(result, encoding='utf-8')
    print(f'  FIXED: {slug} | sections: {list(seen_keys.keys())} | removed {len(duplicate_sections)} dupes')
    updated.append(slug)

print(f'\nTotal fixed: {len(updated)}/{len(SLUGS)}')
