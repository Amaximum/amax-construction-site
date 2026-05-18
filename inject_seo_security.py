#!/usr/bin/env python3
"""
Inject SEO + Security meta tags into every index.html across the site.

Adds, if missing:
  - <meta name="referrer" content="strict-origin-when-cross-origin">
  - <meta http-equiv="X-Content-Type-Options" content="nosniff">
  - <meta http-equiv="X-Frame-Options" content="SAMEORIGIN">
  - <meta http-equiv="Permissions-Policy" content="...">
  - <meta http-equiv="Content-Security-Policy" content="...">
  - Open Graph: og:type, og:title, og:description, og:url, og:site_name,
      og:image (+ width/height/alt), og:locale
  - Twitter Card: twitter:card, twitter:title, twitter:description,
      twitter:image, twitter:image:alt
  - <link rel="alternate" type="text/plain" title="llms.txt" href=".../llms.txt">

Title and description are read from existing <title> and
<meta name="description"> tags. og:url defaults to existing canonical or
inferred from folder path.

The script is idempotent: it never duplicates a tag that already exists.
"""

import re
from pathlib import Path

BASE = Path(r'c:\Projects\SEO_Tool\amax-construction-site')
SITE = 'https://amaximumconstruction.com'

SKIP_FOLDERS = {'book-now'}  # encoding-broken file

# folder substring -> hero image basename (no extension)
SERVICE_IMG = [
    ('basement-renovation', 'basement-1'),
    ('basement',            'basement-1'),
    ('bathroom-renovation', 'bathroom-1'),
    ('bathroom',            'bathroom-1'),
    ('demolition',          'demolition-1'),
    ('deck-railing',        'deck-railings-1'),
    ('railing',             'deck-railings-1'),
    ('deck-builder',        'deck-1'),
    ('deck-contractor',     'deck-1'),
    ('deck',                'deck-1'),
    ('fence',               'fence-1'),
    ('carpenter',           'carpentry-1'),
    ('carpentry',           'carpentry-1'),
    ('handyman',            'handyman-1'),
    ('electrical',          'electrical-1'),
    ('plumbing',            'plumbing-1'),
    ('painting',            'painting-1'),
    ('excavation',          'excavation-1'),
    ('landscap',            'landscaping-1'),
    ('canopy',              'canopy-1'),
    ('interlock',           'interlocking-1'),
    ('christmas',           'christmas-1'),
    ('general-contractor',  'contractor-1'),
    ('contractor',          'contractor-1'),
    ('home-renovation',     'home-renovation-1'),
    ('renovation',          'renovation-1'),
]

DEFAULT_IMG = 'demolition-1'

SECURITY_TAGS = '''  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta http-equiv="X-Content-Type-Options" content="nosniff">
  <meta http-equiv="X-Frame-Options" content="SAMEORIGIN">
  <meta http-equiv="Permissions-Policy" content="geolocation=(), camera=(), microphone=(), payment=()">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self' https:; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:; font-src 'self' data: https:; connect-src 'self' https:; frame-src https:; object-src 'none'; base-uri 'self'; form-action 'self' https:;">'''


def detect_image(folder):
    n = folder.lower()
    for key, img in SERVICE_IMG:
        if key in n:
            return img
    return DEFAULT_IMG


def get_text(pattern, html, default=''):
    m = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else default


def has(tag_regex, html):
    return re.search(tag_regex, html, re.IGNORECASE) is not None


def process(path):
    folder = path.parent.name
    html = path.read_text(encoding='utf-8')

    # Bail out if no <head>
    head_close = re.search(r'</head>', html, re.IGNORECASE)
    if not head_close:
        return 'no-head'

    # Extract title and description
    title = get_text(r'<title[^>]*>(.*?)</title>', html, 'aMaximum Construction')
    title = re.sub(r'\s+', ' ', title).strip()
    description = get_text(
        r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']',
        html, '')

    # Canonical URL fallback
    canonical = get_text(
        r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',
        html, f'{SITE}/{folder}/')

    img_base = detect_image(folder)
    img_url = f'{SITE}/img/services/{img_base}.jpg'
    img_alt = f'aMaximum Construction services — {folder.replace("-", " ")}'

    # Twitter title trimmed
    tw_title = title if len(title) <= 70 else (title[:67].rsplit(' ', 1)[0] + '…')

    additions = []

    # ---- security headers ----
    if not has(r'http-equiv=["\']X-Content-Type-Options["\']', html):
        additions.append(SECURITY_TAGS)

    # ---- Open Graph ----
    og_to_add = []
    og_pairs = [
        ('type', 'website'),
        ('title', title),
        ('description', description or title),
        ('url', canonical),
        ('site_name', 'aMaximum Construction'),
        ('image', img_url),
        ('image:width', '1200'),
        ('image:height', '800'),
        ('image:alt', img_alt),
        ('locale', 'en_CA'),
    ]
    for prop, val in og_pairs:
        if not has(rf'property=["\']og:{re.escape(prop)}["\']', html):
            esc = (val.replace('&', '&amp;').replace('"', '&quot;')
                       .replace('<', '&lt;').replace('>', '&gt;'))
            og_to_add.append(f'  <meta property="og:{prop}" content="{esc}">')
    if og_to_add:
        additions.append('\n'.join(og_to_add))

    # ---- Twitter Card ----
    tw_to_add = []
    tw_pairs = [
        ('card', 'summary_large_image'),
        ('title', tw_title),
        ('description', description or title),
        ('image', img_url),
        ('image:alt', img_alt),
    ]
    for prop, val in tw_pairs:
        if not has(rf'name=["\']twitter:{re.escape(prop)}["\']', html):
            esc = (val.replace('&', '&amp;').replace('"', '&quot;')
                       .replace('<', '&lt;').replace('>', '&gt;'))
            tw_to_add.append(f'  <meta name="twitter:{prop}" content="{esc}">')
    if tw_to_add:
        additions.append('\n'.join(tw_to_add))

    # ---- llms.txt link ----
    if not has(r'href=["\'][^"\']*llms\.txt["\']', html):
        additions.append(
            f'  <link rel="alternate" type="text/plain" title="llms.txt" href="{SITE}/llms.txt">')

    if not additions:
        return 'unchanged'

    insertion = '\n' + '\n'.join(additions) + '\n'
    new_html = html[:head_close.start()] + insertion + html[head_close.start():]
    path.write_bytes(new_html.encode('utf-8'))
    return 'updated'


def main():
    targets = []
    for child in sorted(BASE.iterdir()):
        if not child.is_dir() or child.name.startswith('.') or child.name in SKIP_FOLDERS:
            continue
        idx = child / 'index.html'
        if idx.is_file():
            targets.append(idx)

    # Also handle root index.html
    root_idx = BASE / 'index.html'
    if root_idx.is_file():
        targets.insert(0, root_idx)

    print(f'Scanning {len(targets)} pages...\n')
    counts = {}
    for p in targets:
        try:
            status = process(p)
        except Exception as e:
            status = f'error: {e}'
        counts[status] = counts.get(status, 0) + 1

    print('Summary:')
    for k, v in sorted(counts.items()):
        print(f'  {k:15} {v}')


if __name__ == '__main__':
    main()
