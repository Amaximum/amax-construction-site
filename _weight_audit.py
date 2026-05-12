import os
from pathlib import Path

root = Path('.')
EXCL = {'.git', '.venv', 'node_modules', '__pycache__'}

heavy = []
by_ext = {}
for p in root.rglob('*'):
    if not p.is_file():
        continue
    if any(part in EXCL for part in p.parts):
        continue
    try:
        sz = p.stat().st_size
    except OSError:
        continue
    ext = p.suffix.lower() or '(none)'
    rec = by_ext.setdefault(ext, [0, 0])
    rec[0] += 1
    rec[1] += sz
    if sz > 150_000:
        heavy.append((sz, str(p).replace('\\', '/')))

print('=== Top 50 heaviest files ===')
for sz, path in sorted(heavy, reverse=True)[:50]:
    print(f'{sz/1024:>9.1f} KB  {path}')

print()
print('=== Totals by extension (top 15 by total size) ===')
rows = sorted(by_ext.items(), key=lambda x: -x[1][1])[:15]
for ext, (cnt, sz) in rows:
    print(f'{ext:>10}  files={cnt:<6} total={sz/1024/1024:>7.2f} MB  avg={sz/cnt/1024:>8.1f} KB')
