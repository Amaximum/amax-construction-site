"""Audit: find FAQ content shared across DIFFERENT pages (cross-page duplication).

Extracts the FAQPage question set from each page and groups pages by identical
FAQ content. Reports groups where the same FAQ appears on 2+ different URLs.
Read-only.
"""
import os, re
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP = {'.git', 'node_modules', '.venv', '__pycache__'}

faq_block = re.compile(
    r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)
q_re = re.compile(r'"name"\s*:\s*"(.*?)"', re.S)

groups = defaultdict(list)   # fingerprint -> [rel,...]
page_count = 0

for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in SKIP]
    for f in fn:
        if not f.lower().endswith('.html'):
            continue
        p = os.path.join(dp, f)
        raw = open(p, encoding='utf-8', errors='replace').read()
        rel = os.path.relpath(p, ROOT).replace(os.sep, '/')
        # gather all FAQ question texts on the page
        qs = []
        for m in faq_block.finditer(raw):
            body = m.group(1)
            if '"FAQPage"' not in body:
                continue
            qs.extend(q_re.findall(body))
        if not qs:
            continue
        page_count += 1
        fp = ' || '.join(q.strip().lower() for q in qs)
        groups[fp].append((rel, len(qs)))

dupe_groups = {fp: pages for fp, pages in groups.items() if len(pages) > 1}

print(f'Pages with FAQ schema         : {page_count}')
print(f'Distinct FAQ question-sets    : {len(groups)}')
print(f'Shared-across-pages groups    : {len(dupe_groups)}')
print(f'Pages sharing a FAQ with others: {sum(len(v) for v in dupe_groups.values())}')
print('\n=== SHARED FAQ GROUPS (same Q-set on multiple URLs) ===')
for fp, pages in sorted(dupe_groups.items(), key=lambda x: -len(x[1])):
    rels = [r for r, _ in pages]
    sample_q = fp.split(' || ')[0][:70]
    print(f'\n[{len(pages)} pages] first Q: "{sample_q}..."')
    for r in rels:
        print('   ', r)
