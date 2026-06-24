import os, re
from collections import Counter
ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP = {'.git','node_modules','.venv','__pycache__'}
miss_og, miss_tw = [], []
for dp,dn,fn in os.walk(ROOT):
    dn[:]=[d for d in dn if d not in SKIP]
    for f in fn:
        if f.lower().endswith('.html'):
            p=os.path.join(dp,f)
            raw=open(p,encoding='utf-8',errors='replace').read()
            noindex='noindex' in raw.lower()
            r=os.path.relpath(p,ROOT)
            if not re.search(r'property=["\']og:image["\']',raw,re.I):
                miss_og.append((r,'NOINDEX' if noindex else 'INDEXED'))
            if not re.search(r'name=["\']twitter:image["\']',raw,re.I):
                miss_tw.append((r,'NOINDEX' if noindex else 'INDEXED'))

print('=== og:image missing:', len(miss_og), Counter(s for _,s in miss_og))
print('--- INDEXED (SEO-relevant) ---')
for r,s in sorted(miss_og):
    if s=='INDEXED': print('  ',r)
print()
print('=== twitter:image missing:', len(miss_tw), Counter(s for _,s in miss_tw))
print('--- INDEXED (SEO-relevant) ---')
for r,s in sorted(miss_tw):
    if s=='INDEXED': print('  ',r)
