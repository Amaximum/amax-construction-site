import os, re, json
from pathlib import Path

root = Path('.')

# 18 canonical service hubs
SERVICE_HUBS = {
    'deck-builder': 'Deck Building',
    'deck-railings': 'Deck Railings',
    'fence-contractor-in-toronto': 'Fence Installation',
    'bathroom-renovation': 'Bathroom Renovation',
    'basement-renovation-service-in-toronto': 'Basement Renovation',
    'handyman-plumbing-services': 'Plumbing',
    'canopy': 'Canopy & Awnings',
    'landscaping-services-toronto': 'Landscaping',
    'general-contractor-in-toronto': 'General Contractor',
    'handyman-service-in-toronto': 'Handyman',
    'interlocking-paver-services': 'Interlocking',
    'carpenter-services': 'Carpentry',
    'electrical-handyman-services': 'Electrical',
    'handyman-painting-services': 'Painting',
    'demolition-services': 'Demolition',
    'excavation-services': 'Excavation',
    'home-renovation': 'Home Renovation',
    'christmas-lights-installation-toronto-gta': 'Christmas Lights',
}

SERVICE_HUB_DIRS = set(SERVICE_HUBS.keys())
LOCATION_HUB_DIRS = {'locations'}
KNOWN_SKIP = {'', 'css', 'js', 'images', 'assets', 'fonts', '__pycache__', '.venv', '.git'}

stats = {
    'service_hubs': [],
    'local_service_pages': [],  # e.g. basement-renovation-service-in-markham
    'blog_pages': [],
    'location_hubs': [],
}

# Patterns
def has_related_blogs(html):
    return bool(re.search(r'related.*blog|related.*article|id=["\']related', html, re.I))

def has_service_hub_link(html, hub_slug):
    return f'/{hub_slug}/' in html or f'href="/{hub_slug}"' in html

def links_to_any_hub(html):
    for slug in SERVICE_HUB_DIRS:
        if f'/{slug}/' in html or f'href="/{slug}"' in html:
            return True
    return False

# Detect page type by slug
def classify_dir(dirname):
    if dirname in SERVICE_HUB_DIRS:
        return 'service_hub'
    if dirname.startswith('locations'):
        return 'location_hub'
    # local service pages: contain service keywords + city name
    cities = ['toronto','markham','richmond-hill','scarborough','north-york','etobicoke','vaughan','newmarket','aurora','east-york','woodbridge','mississauga','brampton','oakville']
    service_kw = ['basement','bathroom','deck','fence','landscaping','handyman','renovation','contractor','plumbing','electrical','painting','demolition','excavation','interlocking','carpenter','canopy','christmas']
    has_city = any(c in dirname for c in cities)
    has_svc = any(s in dirname for s in service_kw)
    if has_city and has_svc:
        return 'local_service'
    # blogs: remaining pages with index.html
    return 'blog'

results = {'local_service_missing_hub': [], 'local_service_missing_blog': [], 'blog_missing_service': [], 'blog_missing_related': []}

for d in root.iterdir():
    if not d.is_dir():
        continue
    name = d.name
    if name in KNOWN_SKIP or name.startswith('.'):
        continue
    idx = d / 'index.html'
    if not idx.exists():
        continue
    
    html = idx.read_text(encoding='utf-8', errors='ignore')
    ptype = classify_dir(name)
    
    if ptype == 'local_service':
        # find which hub it belongs to
        parent_hub = None
        for slug in SERVICE_HUB_DIRS:
            base = slug.replace('-service-in-toronto','').replace('-in-toronto','').replace('-toronto','').replace('-services','').replace('-service','')
            if base and base in name:
                parent_hub = slug
                break
        has_hub = has_service_hub_link(html, parent_hub) if parent_hub else links_to_any_hub(html)
        has_blog = has_related_blogs(html)
        if not has_hub:
            results['local_service_missing_hub'].append({'page': name, 'hub': parent_hub})
        if not has_blog:
            results['local_service_missing_blog'].append(name)
    
    elif ptype == 'blog':
        has_svc = links_to_any_hub(html)
        has_blog = has_related_blogs(html)
        if not has_svc:
            results['blog_missing_service'].append(name)
        if not has_blog:
            results['blog_missing_related'].append(name)

print(f"LOCAL SERVICE pages missing hub link: {len(results['local_service_missing_hub'])}")
for x in results['local_service_missing_hub'][:10]:
    print(f"  {x['page']} (hub: {x['hub']})")

print(f"\nLOCAL SERVICE pages missing related blogs: {len(results['local_service_missing_blog'])}")
for x in results['local_service_missing_blog'][:10]:
    print(f"  {x}")

print(f"\nBLOG pages missing service link: {len(results['blog_missing_service'])}")
for x in results['blog_missing_service'][:10]:
    print(f"  {x}")

print(f"\nBLOG pages missing related articles: {len(results['blog_missing_related'])}")
for x in results['blog_missing_related'][:10]:
    print(f"  {x}")

print("\n--- SUMMARY ---")
print(json.dumps({k: len(v) for k,v in results.items()}, indent=2))
