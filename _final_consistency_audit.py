import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {'.git', 'node_modules', '.venv', '__pycache__'}

html_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        if fn.lower().endswith('.html'):
            html_files.append(os.path.join(dirpath, fn))

def rel(p): return os.path.relpath(p, ROOT)

issues = {
    'old_phone_416': [],     # 4165793576 appearing as a CALL/tel (not whatsapp)
    'old_phone_647': [],     # 6479678555 anywhere
    'bad_email': [],         # emails not in allowed list
    'double_amp': [],        # &amp;amp;
    'old_jsver': [],         # site.js?v not 20260624a
    'missing_title': [],
    'missing_desc': [],
    'missing_canonical': [],
    'missing_h1': [],
    'missing_og_title': [],
    'missing_og_desc': [],
    'missing_tw_title': [],
    'missing_tw_desc': [],
    'missing_og_image': [],
    'missing_tw_image': [],
}

ALLOWED_EMAILS = {'amaximumconstructioncorp@gmail.com', 'care@amaximumconstruction.com'}
email_re = re.compile(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}')

total = 0
for f in html_files:
    total += 1
    raw = open(f, encoding='utf-8', errors='replace').read()
    low = raw.lower()
    r = rel(f)

    # phone: 416 old line used as a CALL (tel:) is wrong; whatsapp is allowed
    for m in re.finditer(r'tel:\+?1?416\s*579\s*3576', raw):
        issues['old_phone_416'].append(r); break
    if re.search(r'647\s*[\-.]?\s*967\s*[\-.]?\s*8555|16479678555', raw):
        issues['old_phone_647'].append(r)

    for em in set(email_re.findall(raw)):
        eml = em.lower()
        if eml.endswith(('.png','.jpg','.jpeg','.webp','.svg','.gif','.css','.js')):
            continue
        if '@' in eml and eml not in ALLOWED_EMAILS and 'example' not in eml and 'sentry' not in eml and 'schema.org' not in eml:
            # only flag plausible contact emails
            if 'amaximum' in eml or 'gmail' in eml or 'construction' in eml:
                issues['bad_email'].append(f'{r} :: {em}')

    if '&amp;amp;' in raw:
        issues['double_amp'].append(r)

    if 'site.js?v=' in raw and 'site.js?v=20260624a' not in raw:
        issues['old_jsver'].append(r)

    # SEO essentials
    if not re.search(r'<title[^>]*>.*?</title>', raw, re.I|re.S):
        issues['missing_title'].append(r)
    if not re.search(r'<meta[^>]+name=["\']description["\']', raw, re.I):
        issues['missing_desc'].append(r)
    if not re.search(r'<link[^>]+rel=["\']canonical["\']', raw, re.I):
        issues['missing_canonical'].append(r)
    if not re.search(r'<h1[\s>]', raw, re.I):
        issues['missing_h1'].append(r)
    if not re.search(r'property=["\']og:title["\']', raw, re.I):
        issues['missing_og_title'].append(r)
    if not re.search(r'property=["\']og:description["\']', raw, re.I):
        issues['missing_og_desc'].append(r)
    if not re.search(r'name=["\']twitter:title["\']', raw, re.I):
        issues['missing_tw_title'].append(r)
    if not re.search(r'name=["\']twitter:description["\']', raw, re.I):
        issues['missing_tw_desc'].append(r)
    if not re.search(r'property=["\']og:image["\']', raw, re.I):
        issues['missing_og_image'].append(r)
    if not re.search(r'name=["\']twitter:image["\']', raw, re.I):
        issues['missing_tw_image'].append(r)

print(f'TOTAL HTML FILES: {total}\n')
for k, v in issues.items():
    print(f'{k:22} : {len(v)}')
print('\n--- DETAILS (first 15 each) ---')
for k, v in issues.items():
    if v:
        print(f'\n[{k}] ({len(v)})')
        for x in v[:15]:
            print('   ', x)
        if len(v) > 15:
            print(f'    ... +{len(v)-15} more')
