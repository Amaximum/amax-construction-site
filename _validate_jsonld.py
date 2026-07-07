# -*- coding: utf-8 -*-
import json, re, sys, os
ROOT = os.path.dirname(os.path.abspath(__file__))
files = [
 'handyman-plumbing-services','plumbing-services-in-toronto',
 'general-contractor-services','general-contractor-services-near-me',
 'renovation-service','renovation-services-in-toronto-gta',
 'basement-bathroom-renovation-richmond-hill','bathroom-renovation-richmond-hill',
 'painting-services-in-markham','painting-services-in-newmarket',
 'painting-services-in-richmond-hill','painting-services-in-vaughan','painting-services-in-toronto',
]
blk = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
bad = 0
for slug in files:
    p = os.path.join(ROOT, slug, 'index.html')
    raw = open(p, encoding='utf-8').read()
    for i, m in enumerate(blk.findall(raw)):
        try:
            json.loads(m.strip())
        except Exception as e:
            bad += 1
            print(f'INVALID {slug} block {i}: {e}')
print('all valid' if bad == 0 else f'{bad} invalid blocks')
sys.stdout.reconfigure(encoding='utf-8')
