# -*- coding: utf-8 -*-
"""Fingerprint every page's FAQ question set; report duplicate clusters."""
import os, re, sys, glob
ROOT = os.path.dirname(os.path.abspath(__file__))
q_re = re.compile(r'"@type":\s*"Question"[^}]*?"name":\s*"([^"]+)"', re.S)

groups = {}
for path in glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True):
    raw = open(path, encoding='utf-8', errors='ignore').read()
    qs = [q.strip().lower() for q in q_re.findall(raw)]
    if not qs:
        continue
    fp = ' || '.join(qs)
    groups.setdefault(fp, []).append(os.path.relpath(path, ROOT))

dups = {fp: files for fp, files in groups.items() if len(files) > 1}
print(f'pages with FAQ: {sum(len(v) for v in groups.values())}')
print(f'unique fingerprints: {len(groups)}')
print(f'duplicate clusters: {len(dups)}\n')
for i, (fp, files) in enumerate(sorted(dups.items(), key=lambda x: -len(x[1])), 1):
    print(f'--- cluster {i} ({len(files)} pages) ---')
    print('  Q1:', fp.split(' || ')[0][:70])
    for f in files:
        print('   ', f)
    print()

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
