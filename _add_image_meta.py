import os, re, html as htmlmod

ROOT = os.path.dirname(os.path.abspath(__file__))

# image mapping by relative path (normalized with forward slashes)
def pick_image(rel):
    rel = rel.replace('\\', '/')
    table = {
        'blog/basement-renovation-ideas/index.html': 'basement-1.jpg',
        'blog/bathroom-renovation-guide/index.html': 'bathroom-1.jpg',
        'blog/contractor-selection-guide/index.html': 'contractor-1.jpg',
        'blog/deck-maintenance-tips/index.html': 'deck-1.jpg',
        'blog/fence-installation-options/index.html': 'fence-1.jpg',
        'blog/plumbing-emergency-guide/index.html': 'plumbing-1.jpg',
        'services/handyman-plumbing.html': 'handyman-1.jpg',
        'services/handyman-plumbing/index.html': 'handyman-1.jpg',
    }
    if rel in table:
        return f'https://www.amaximumconstruction.com/img/services/{table[rel]}'
    if rel.startswith('locations/'):
        # location hubs list every service -> use the general renovation image
        return 'https://www.amaximumconstruction.com/img/services/home-renovation-1.jpg'
    return None

BASE = 'https://www.amaximumconstruction.com/img/'

# targets = the 41 indexed pages found by audit (excluding service-template.html)
targets = []
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in {'.git', 'node_modules', '.venv', '__pycache__'}]
    for f in fn:
        if not f.lower().endswith('.html'):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT)
        if rel.replace('\\', '/') == 'services/service-template.html':
            continue
        raw = open(p, encoding='utf-8', errors='replace').read()
        if 'noindex' in raw.lower():
            continue
        has_ogimg = re.search(r'property=["\']og:image["\']', raw, re.I)
        has_twimg = re.search(r'name=["\']twitter:image["\']', raw, re.I)
        if has_ogimg and has_twimg:
            continue
        img = pick_image(rel)
        if not img:
            continue
        targets.append((p, rel, img))

def get_attr(raw, prop_kind, name):
    # prop_kind = 'property' or 'name'
    m = re.search(rf'{prop_kind}=["\']{re.escape(name)}["\'][^>]*content=["\'](.*?)["\']', raw, re.I)
    if not m:
        m = re.search(rf'content=["\'](.*?)["\'][^>]*{prop_kind}=["\']{re.escape(name)}["\']', raw, re.I)
    return m.group(1) if m else None

changed = 0
for p, rel, img in targets:
    raw = open(p, encoding='utf-8', errors='replace').read()
    orig = raw
    ogt_for_alt = get_attr(raw, 'property', 'og:title') or 'aMaximum Construction'
    alt_esc = ogt_for_alt  # already HTML-escaped as stored in the attribute

    og_block = (
        f'  <meta property="og:image" content="{img}">\n'
        f'  <meta property="og:image:width" content="1200">\n'
        f'  <meta property="og:image:height" content="800">\n'
        f'  <meta property="og:image:alt" content="{alt_esc}">\n'
    )

    # 1) add og:image after og:site_name (or after og:url) if missing
    if not re.search(r'property=["\']og:image["\']', raw, re.I):
        m = re.search(r'([ \t]*<meta property=["\']og:site_name["\'][^>]*>\n)', raw, re.I)
        if not m:
            m = re.search(r'([ \t]*<meta property=["\']og:url["\'][^>]*>\n)', raw, re.I)
        if m:
            raw = raw[:m.end()] + og_block + raw[m.end():]

    # 2) twitter: if no twitter:card at all, add full card; else add twitter:image
    has_tw_card = re.search(r'name=["\']twitter:card["\']', raw, re.I)
    if not re.search(r'name=["\']twitter:image["\']', raw, re.I):
        if has_tw_card:
            # insert twitter:image after twitter:description (or after twitter:card)
            m = re.search(r'([ \t]*<meta name=["\']twitter:description["\'][^>]*>\n)', raw, re.I)
            if not m:
                m = re.search(r'([ \t]*<meta name=["\']twitter:card["\'][^>]*>\n)', raw, re.I)
            if m:
                tw_img = (
                    f'  <meta name="twitter:image" content="{img}">\n'
                    f'  <meta name="twitter:image:alt" content="{alt_esc}">\n'
                )
                raw = raw[:m.end()] + tw_img + raw[m.end():]
        else:
            # build full twitter card, mirroring og:title / og:description
            ogt = get_attr(raw, 'property', 'og:title') or ''
            ogd = get_attr(raw, 'property', 'og:description') or ''
            tw_full = (
                f'  <meta name="twitter:card" content="summary_large_image">\n'
                f'  <meta name="twitter:title" content="{ogt}">\n'
                f'  <meta name="twitter:description" content="{ogd}">\n'
                f'  <meta name="twitter:image" content="{img}">\n'
                f'  <meta name="twitter:image:alt" content="{alt_esc}">\n'
            )
            # insert right after the og:image block (after og:image:alt) or after og:site_name
            m = re.search(r'([ \t]*<meta property=["\']og:image:alt["\'][^>]*>\n)', raw, re.I)
            if not m:
                m = re.search(r'([ \t]*<meta property=["\']og:site_name["\'][^>]*>\n)', raw, re.I)
            if m:
                raw = raw[:m.end()] + tw_full + raw[m.end():]

    if raw != orig:
        open(p, 'w', encoding='utf-8').write(raw)
        changed += 1
        print('FIXED', rel)

print(f'\nTOTAL FIXED: {changed} / {len(targets)} targets')
