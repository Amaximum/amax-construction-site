import re
from pathlib import Path
samples = [
    'interlocking-stone-services-in-richmond-hill',
    'home-renovation-newmarket',
    'fence-contractor-in-richmond-hill',
    'carpenter-services-markham',
    'demolition-service-in-toronto',
    'bathroom-renovation-aurora',
    'handyman-charges',
    'what-we-do',
    'deck-builder-schomberg',
    'demolition-services-nobleton',
    'carpenter-services-aurora',
    'carpenter-services-vaughan',
    'carpenter-services-toronto',
    'demolition-services-oakville',
    'demolition-services-scarborough',
]
for s in samples:
    p = Path(s) / 'index.html'
    if not p.exists():
        print(f'{s:50s}  MISSING'); continue
    t = p.read_text(encoding='utf-8', errors='ignore')
    canon = re.search(r'rel="canonical" href="([^"]+)"', t)
    robots = re.search(r'name="robots" content="([^"]+)"', t)
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.DOTALL)
    body = re.sub(r'<script.*?</script>', '', t, flags=re.DOTALL)
    body = re.sub(r'<style.*?</style>', '', body, flags=re.DOTALL)
    body = re.sub(r'<[^>]+>', ' ', body)
    body = re.sub(r'\s+', ' ', body).strip()
    canon_txt = canon.group(1) if canon else 'NONE'
    canon_ok = 'OK' if canon and s in canon_txt else f'OTHER->{canon_txt}'
    robots_txt = robots.group(1) if robots else 'default'
    h1_txt = (h1.group(1)[:60].strip() if h1 else 'NONE')
    print(f'{s:50s}  len={len(body):5d}  canon={canon_ok:50s}  robots={robots_txt:20s}  h1={h1_txt}')
