"""
Inject "Related Articles" sections into pages that are missing them.
Only touches real blog/local-service pages, skips utility pages.
Does NOT create new pages — only links to existing ones.
"""
import re
import os
from pathlib import Path

root = Path('.')

# ─── Pages to skip (utility / indexes) ───────────────────────────────────────
SKIP_PAGES = {
    'blog', 'book-now', 'client-testimonials', 'company-policy-of-amaximum-construction',
    'our-work-process', 'portfolio', 'sitemap', 'thank-you-page', 'what-we-do',
    'why-choose-us', 'amaximum-deck-builder-blog',
}

# ─── 18 canonical service hubs ────────────────────────────────────────────────
SERVICE_HUB_DIRS = {
    'deck-builder', 'deck-railings', 'fence-contractor-in-toronto', 'bathroom-renovation',
    'basement-renovation-service-in-toronto', 'handyman-plumbing-services', 'canopy',
    'landscaping-services-toronto', 'general-contractor-in-toronto', 'handyman-service-in-toronto',
    'interlocking-paver-services', 'carpenter-services', 'electrical-handyman-services',
    'handyman-painting-services', 'demolition-services', 'excavation-services',
    'home-renovation', 'christmas-lights-installation-toronto-gta',
}

KNOWN_SKIP = {'', 'css', 'js', 'images', 'assets', 'fonts', '__pycache__', '.venv', '.git', 'locations'}

# ─── Service topic detection (slug keywords → topic) ─────────────────────────
TOPIC_KEYWORDS = {
    'deck':        ['deck', 'rainescape', 'trex', 'decking', 'deck-board', 'deck-railing'],
    'basement':    ['basement', 'below-grade', 'in-law suite'],
    'bathroom':    ['bathroom', 'bath-reno', 'accessorizing-renovated'],
    'handyman':    ['handyman', 'drywall-repair', 'furniture-assembly', 'repair'],
    'landscaping': ['landscaping', 'landscape', 'garden', 'backyard-oasis'],
    'fence':       ['fence', 'privacy-screen', 'fencing'],
    'interlocking':['interlocking', 'paving', 'paver', 'pavement', 'paving-company'],
    'renovation':  ['renovation', 'home-renovation', 'remodel', 'affordable-home'],
    'contractor':  ['contractor', 'general-contractor', 'avoiding-general'],
    'christmas':   ['christmas', 'holiday-lights', 'christmas-lights'],
    'carpentry':   ['carpentry', 'carpenter', 'woodwork'],
    'canopy':      ['canopy', 'awning'],
    'demolition':  ['demolition', 'demo'],
    'excavation':  ['excavation', 'excavating'],
    'electrical':  ['electrical', 'electrician'],
    'painting':    ['painting', 'paint'],
    'plumbing':    ['plumbing', 'plumber'],
}

# ─── Service hub URL for each topic ───────────────────────────────────────────
TOPIC_HUB = {
    'deck':        '/deck-builder/',
    'basement':    '/basement-renovation-service-in-toronto/',
    'bathroom':    '/bathroom-renovation/',
    'handyman':    '/handyman-service-in-toronto/',
    'landscaping': '/landscaping-services-toronto/',
    'fence':       '/fence-contractor-in-toronto/',
    'interlocking':'/interlocking-paver-services/',
    'renovation':  '/home-renovation/',
    'contractor':  '/general-contractor-in-toronto/',
    'christmas':   '/christmas-lights-installation-toronto-gta/',
    'carpentry':   '/carpenter-services/',
    'canopy':      '/canopy/',
    'demolition':  '/demolition-services/',
    'excavation':  '/excavation-services/',
    'electrical':  '/electrical-handyman-services/',
    'painting':    '/handyman-painting-services/',
    'plumbing':    '/handyman-plumbing-services/',
}

TOPIC_LABEL = {
    'deck': 'Deck Building', 'basement': 'Basement Renovation', 'bathroom': 'Bathroom Renovation',
    'handyman': 'Handyman Services', 'landscaping': 'Landscaping', 'fence': 'Fence Installation',
    'interlocking': 'Interlocking & Paving', 'renovation': 'Home Renovation',
    'contractor': 'General Contractor', 'christmas': 'Christmas Lights',
    'carpentry': 'Carpentry', 'canopy': 'Canopy & Awnings', 'demolition': 'Demolition',
    'excavation': 'Excavation', 'electrical': 'Electrical', 'painting': 'Painting',
    'plumbing': 'Plumbing',
}


def detect_topic(slug, title=''):
    text = (slug + ' ' + title).lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return topic
    return None


def has_related(html):
    return bool(re.search(r'related.{0,20}(blog|article)|id="related', html, re.I))


def get_title(html, slug):
    m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
    if m:
        t = m.group(1)
        # Strip " | aMaximum Construction" suffix
        t = re.sub(r'\s*[|–-]\s*aMaximum.*$', '', t, flags=re.I)
        return t.strip()
    return slug.replace('-', ' ').title()


def classify(name):
    if name in SERVICE_HUB_DIRS:
        return 'hub'
    if name.startswith('location'):
        return 'location'
    cities = ['toronto', 'markham', 'richmond-hill', 'scarborough', 'north-york',
              'etobicoke', 'vaughan', 'newmarket', 'aurora', 'east-york', 'woodbridge']
    service_kw = ['basement', 'bathroom', 'deck', 'fence', 'landscaping', 'handyman',
                  'renovation', 'contractor', 'plumbing', 'electrical', 'painting',
                  'demolition', 'excavation', 'interlocking', 'carpenter', 'canopy', 'christmas']
    if any(c in name for c in cities) and any(s in name for s in service_kw):
        return 'local_svc'
    return 'blog'


# ─── Step 1: Build index of all existing blog/local_svc pages with topics ────
page_index = {}  # slug -> {topic, title, url}

for d in sorted(root.iterdir()):
    if not d.is_dir():
        continue
    name = d.name
    if name in KNOWN_SKIP or name.startswith('.') or name in SKIP_PAGES:
        continue
    idx = d / 'index.html'
    if not idx.exists():
        continue
    html = idx.read_text(encoding='utf-8', errors='ignore')
    ptype = classify(name)
    if ptype in ('blog', 'local_svc'):
        title = get_title(html, name)
        topic = detect_topic(name, title)
        page_index[name] = {'type': ptype, 'topic': topic, 'title': title, 'url': f'/{name}/'}


# ─── Step 2: Group slugs by topic ─────────────────────────────────────────────
by_topic = {}
for slug, info in page_index.items():
    t = info['topic'] or 'general'
    by_topic.setdefault(t, []).append(slug)


def get_related(current_slug, topic, max_n=3):
    candidates = by_topic.get(topic, []) + by_topic.get('general', [])
    # Remove current page
    others = [s for s in candidates if s != current_slug]
    return others[:max_n]


def make_related_section(slug, topic):
    related = get_related(slug, topic)
    if not related:
        return None

    hub_url = TOPIC_HUB.get(topic, '/')
    hub_label = TOPIC_LABEL.get(topic, 'Our Services')

    cards_html = ''
    for r in related:
        info = page_index.get(r, {})
        title = info.get('title', r.replace('-', ' ').title())
        url = f'/{r}/'
        cards_html += f'\n      <a href="{url}" class="card"><h3>{title}</h3></a>'

    section = f'''
<section class="island reveal related-articles" id="related-articles" aria-label="Related articles">
  <div class="section-head"><h2>Related Articles</h2></div>
  <div class="cards">{cards_html}
  </div>
  <p style="text-align:center;margin-top:1rem;"><a href="{hub_url}" class="btn-primary">{hub_label} →</a></p>
</section>
'''
    return section


# ─── Step 3: Inject where missing ─────────────────────────────────────────────
updated = []
skipped_no_topic = []

for slug, info in page_index.items():
    idx = root / slug / 'index.html'
    html = idx.read_text(encoding='utf-8', errors='ignore')

    if has_related(html):
        continue  # already has related section

    topic = info['topic']
    if not topic:
        skipped_no_topic.append(slug)
        continue

    section = make_related_section(slug, topic)
    if not section:
        skipped_no_topic.append(slug)
        continue

    # Insert before </footer>
    if '</footer>' in html:
        new_html = html.replace('</footer>', section + '</footer>', 1)
    else:
        # Fallback: before </body>
        new_html = html.replace('</body>', section + '</body>', 1)

    idx.write_text(new_html, encoding='utf-8')
    updated.append(slug)
    print(f'  UPDATED: {slug}  (topic: {topic})')


print(f'\nTotal updated: {len(updated)}')
if skipped_no_topic:
    print(f'Skipped (no topic detected): {skipped_no_topic}')
