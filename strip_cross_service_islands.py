"""
Remove cross-service promo islands from all service hub pages.
Targets sections whose <h2> text equals "Our Other Services", "Related Service",
or "Related Services". Hubs only — does not touch homepage, locations, or blog.
"""
import re
from pathlib import Path

HUBS = [
    'handyman-services', 'deck-builder', 'basement-renovation', 'bathroom-renovation',
    'fence-installation', 'interlocking-paver-services', 'landscaping-services',
    'demolition-services', 'general-contractor-services', 'home-renovation',
    'carpenter-services', 'renovation-service', 'excavation-services', 'deck-railings',
    'christmas-lights-installation-toronto-gta', 'canopy', 'paving-company',
    'professional-demolition-services', 'electrical-handyman-services',
    'handyman-plumbing-services',
]

TARGET_HEADINGS = {'our other services', 'related service', 'related services'}

# Greedy-but-balanced removal: match <section ...> ... </section> that contains
# one of the target H2s. Sections in this codebase don't nest, so this is safe.
SECTION_RE = re.compile(
    r'[ \t]*<section\b[^>]*>.*?</section>\s*\n?',
    re.IGNORECASE | re.DOTALL,
)
H2_RE = re.compile(r'<h2[^>]*>\s*(.*?)\s*</h2>', re.IGNORECASE | re.DOTALL)

def strip_html(s: str) -> str:
    return re.sub(r'<[^>]+>', '', s).strip().lower()

total_removed = 0
files_changed = 0
for hub in HUBS:
    p = Path(hub) / 'index.html'
    if not p.exists():
        print(f'  skip (missing): {hub}')
        continue
    html = p.read_text(encoding='utf-8')
    original = html

    def replace(m: re.Match) -> str:
        block = m.group(0)
        h2 = H2_RE.search(block)
        if not h2:
            return block
        text = strip_html(h2.group(1))
        if text in TARGET_HEADINGS:
            return ''
        return block

    new_html = SECTION_RE.sub(replace, html)
    removed = (original.count('<section') - new_html.count('<section'))
    if new_html != original:
        p.write_bytes(new_html.encode('utf-8'))
        total_removed += removed
        files_changed += 1
        print(f'  {hub}: removed {removed} section(s)')
    else:
        print(f'  {hub}: nothing to remove')

print(f'\nDone. Files changed: {files_changed}. Sections removed: {total_removed}.')
