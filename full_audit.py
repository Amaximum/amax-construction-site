import re
from pathlib import Path

root = Path('.')
SERVICE_HUB_DIRS = {
    'deck-builder','deck-railings','fence-contractor-in-toronto','bathroom-renovation',
    'basement-renovation-service-in-toronto','handyman-plumbing-services','canopy',
    'landscaping-services-toronto','general-contractor-in-toronto','handyman-service-in-toronto',
    'interlocking-paver-services','carpenter-services','electrical-handyman-services',
    'handyman-painting-services','demolition-services','excavation-services',
    'home-renovation','christmas-lights-installation-toronto-gta'
}
KNOWN_SKIP = {'','css','js','images','assets','fonts','__pycache__','.venv','.git'}
cities = ['toronto','markham','richmond-hill','scarborough','north-york','etobicoke',
          'vaughan','newmarket','aurora','east-york','woodbridge','mississauga','brampton','oakville']
service_kw = ['basement','bathroom','deck','fence','landscaping','handyman','renovation',
              'contractor','plumbing','electrical','painting','demolition','excavation',
              'interlocking','carpenter','canopy','christmas']

def has_related(html):
    return bool(re.search(r'related.{0,20}(blog|article)|id="related', html, re.I))

def links_hub(html):
    return any(f'/{s}/' in html for s in SERVICE_HUB_DIRS)

def classify(name):
    if name in SERVICE_HUB_DIRS: return 'hub'
    if name.startswith('location'): return 'location'
    if any(c in name for c in cities) and any(s in name for s in service_kw): return 'local_svc'
    return 'blog'

missing_related = []
missing_hub = []
for d in sorted(root.iterdir()):
    if not d.is_dir() or d.name in KNOWN_SKIP or d.name.startswith('.'): continue
    idx = d / 'index.html'
    if not idx.exists(): continue
    html = idx.read_text(encoding='utf-8', errors='ignore')
    t = classify(d.name)
    if t in ('local_svc', 'blog'):
        if not has_related(html):
            missing_related.append(f'[{t}] {d.name}')
        if not links_hub(html):
            missing_hub.append(f'[{t}] {d.name}')

print('=== Missing related articles/blogs ===')
for x in missing_related:
    print(' ', x)
print(f'Total: {len(missing_related)}')

print('\n=== Missing service hub link ===')
for x in missing_hub:
    print(' ', x)
print(f'Total: {len(missing_hub)}')
