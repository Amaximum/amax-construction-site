import os, re
from collections import Counter
ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP = {'.git','node_modules','.venv','__pycache__'}

def walk_html():
    for dp,dn,fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP]
        for f in fn:
            if f.lower().endswith('.html'):
                yield os.path.join(dp,f)

# sitemap URLs
sm = open(os.path.join(ROOT,'sitemap.xml'),encoding='utf-8',errors='replace').read() if os.path.exists(os.path.join(ROOT,'sitemap.xml')) else ''
sitemap_urls = set(re.findall(r'<loc>\s*(.*?)\s*</loc>', sm))

def url_to_relpath(u):
    u = u.split('#')[0].split('?')[0]
    u = re.sub(r'^https?://(www\.)?amaximumconstruction\.com', '', u)
    if u.endswith('/'):
        u += 'index.html'
    elif not u.endswith('.html'):
        u += '/index.html' if not u.endswith('.html') else ''
    return u.lstrip('/').replace('/', os.sep)

problems = {
    'canonical_not_self': [],
    'canonical_non_www': [],
    'noindex_in_sitemap': [],
    'indexed_not_in_sitemap': [],
    'lang_missing': [],
    'viewport_missing': [],
    'img_no_alt': [],
    'no_schema': [],
    'no_breadcrumb_schema': [],
    'multiple_h1': [],
    'robots_meta_missing': [],
}

titles = Counter(); descs = Counter()
title_map = {}; desc_map = {}

def expected_url(rel):
    rel = rel.replace(os.sep,'/')
    if rel.endswith('index.html'):
        path = rel[:-len('index.html')]
    else:
        path = rel
    return 'https://amaximumconstruction.com/' + path

for p in walk_html():
    raw = open(p,encoding='utf-8',errors='replace').read()
    low = raw.lower()
    rel = os.path.relpath(p, ROOT)
    relu = rel.replace(os.sep,'/')
    noindex = 'noindex' in low

    # lang
    if not re.search(r'<html[^>]*\blang=', raw, re.I):
        problems['lang_missing'].append(relu)
    # viewport
    if not re.search(r'name=["\']viewport["\']', raw, re.I):
        problems['viewport_missing'].append(relu)
    # robots meta
    if not re.search(r'name=["\']robots["\']', raw, re.I):
        problems['robots_meta_missing'].append(relu)

    # canonical
    mc = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\'](.*?)["\']', raw, re.I)
    if mc:
        can = mc.group(1).strip()
        if '://www.amaximumconstruction.com' in can or can.startswith('http://'):
            problems['canonical_non_www'].append(f'{relu} -> {can}')
        # self-reference check for index.html pages
        exp = expected_url(rel)
        if not noindex:
            cn = can.rstrip('/') + '/'
            en = exp.rstrip('/') + '/'
            # allow root and exact
            if cn.lower() != en.lower():
                problems['canonical_not_self'].append(f'{relu} -> {can} (exp {exp})')

    # sitemap membership
    in_sm = False
    if mc:
        can = mc.group(1).strip()
        in_sm = can in sitemap_urls or can.rstrip('/') + '/' in sitemap_urls or can.rstrip('/') in sitemap_urls
    if noindex and in_sm:
        problems['noindex_in_sitemap'].append(relu)
    if (not noindex) and (not in_sm) and relu != 'services/service-template.html':
        problems['indexed_not_in_sitemap'].append(relu)

    # schema
    if 'application/ld+json' not in low:
        if not noindex:
            problems['no_schema'].append(relu)
    if 'breadcrumblist' not in low and not noindex and relu not in ('index.html',):
        problems['no_breadcrumb_schema'].append(relu)

    # h1 count
    h1s = len(re.findall(r'<h1[\s>]', raw, re.I))
    if h1s > 1:
        problems['multiple_h1'].append(f'{relu} ({h1s})')

    # images alt (content imgs only, skip data: and svg sprite)
    for im in re.finditer(r'<img\b[^>]*>', raw, re.I):
        tag = im.group(0)
        if not re.search(r'\balt=', tag, re.I):
            problems['img_no_alt'].append(relu)
            break

    # duplicate title/desc (indexed only)
    if not noindex:
        mt = re.search(r'<title[^>]*>(.*?)</title>', raw, re.I|re.S)
        if mt:
            t = mt.group(1).strip()
            titles[t]+=1; title_map.setdefault(t,[]).append(relu)
        md = re.search(r'name=["\']description["\'][^>]*content=["\'](.*?)["\']', raw, re.I|re.S)
        if md:
            d = md.group(1).strip()
            descs[d]+=1; desc_map.setdefault(d,[]).append(relu)

print('SITEMAP <loc> count:', len(sitemap_urls))
for k,v in problems.items():
    print(f'{k:24}: {len(v)}')

dup_titles = {t:f for t,f in title_map.items() if titles[t]>1}
dup_descs = {d:f for d,f in desc_map.items() if descs[d]>1}
print(f'duplicate_titles        : {len(dup_titles)} groups')
print(f'duplicate_descriptions  : {len(dup_descs)} groups')

print('\n=== DETAILS (first 12) ===')
for k,v in problems.items():
    if v:
        print(f'\n[{k}] {len(v)}')
        for x in v[:12]:
            print('   ',x)
        if len(v)>12: print(f'   ... +{len(v)-12} more')

if dup_titles:
    print('\n[duplicate_titles]')
    for t,f in list(dup_titles.items())[:10]:
        print(f'   "{t[:60]}" x{len(f)}: {f[:4]}')
if dup_descs:
    print('\n[duplicate_descriptions]')
    for d,f in list(dup_descs.items())[:10]:
        print(f'   "{d[:60]}" x{len(f)}: {f[:4]}')
