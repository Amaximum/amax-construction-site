import re
from pathlib import Path

samples = [
    'carpenter-services-aurora',
    'carpenter-services-vaughan',
    'demolition-services-nobleton',
    'bathroom-renovation-aurora',
    'deck-builder-schomberg',
    'home-renovation-newmarket',
    'fence-contractor-in-richmond-hill',
    'interlocking-stone-services-in-richmond-hill',
    'handyman-service-in-aurora',
    'handyman-service-in-richmond-hill',
]

# Find href targets that look like service or location pages.
for s in samples:
    p = Path(s) / 'index.html'
    if not p.exists():
        print(f'{s}  MISSING'); continue
    t = p.read_text(encoding='utf-8', errors='ignore')
    hrefs = re.findall(r'href="(/[^"#?]+/?)"', t)
    # de-dupe and exclude self
    self_path = '/' + s + '/'
    hrefs = [h for h in hrefs if h != self_path]
    services = [h for h in set(hrefs) if re.search(r'(service|contractor|builder|installer|renovation|handyman|carpenter|demolition|landscaping|painting|plumbing|electrical|fence|deck|bathroom|basement|interlock|excavation|canopy|christmas)', h)]
    locations = [h for h in set(hrefs) if h.startswith('/locations/')]
    print(f'{s:50s}  total-internal={len(set(hrefs)):3d}  service-like={len(services):3d}  locations={len(locations):3d}')
    # quick sample
    print('   services sample:', sorted(services)[:6])
    print('   locations sample:', sorted(locations)[:6])
