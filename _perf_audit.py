import re
from pathlib import Path
from collections import defaultdict

root = Path('.')

img_re = re.compile(r'''(?:src|href|content|data-src|srcset|poster)=["']([^"']+\.(?:jpe?g|png|webp|gif|svg|avif))["']''', re.I)
css_url_re = re.compile(r'''url\(([^)]+\.(?:jpe?g|png|webp|gif|svg|avif))\)''', re.I)
script_re = re.compile(r'''<script[^>]*\bsrc=["']([^"']+)["']''', re.I)
link_css_re = re.compile(r'''<link[^>]*\brel=["']stylesheet["'][^>]*\bhref=["']([^"']+)["']''', re.I)
font_re = re.compile(r'''(?:src|href)=["']([^"']+\.(?:woff2?|ttf|otf))["']''', re.I)

ref_count = defaultdict(int)
page_weight = defaultdict(int)  # bytes loaded by page
page_imgs = defaultdict(list)

html_files = [p for p in root.rglob('*.html') if '.git' not in str(p) and '.venv' not in str(p) and 'node_modules' not in str(p)]

def resolve(ref, page_dir):
    if ref.startswith(('http://','https://','//','data:','mailto:','tel:','#')):
        return None
    r = ref.split('?')[0].split('#')[0]
    if r.startswith('/'):
        return (root / r.lstrip('/')).resolve()
    return (page_dir / r).resolve()

for h in html_files:
    try:
        text = h.read_text(encoding='utf-8', errors='ignore')
    except: continue
    refs = set()
    for m in img_re.finditer(text):
        for part in m.group(1).split(','):
            url = part.strip().split()[0]
            refs.add(url)
    for m in css_url_re.finditer(text):
        refs.add(m.group(1).strip().strip('"\''))
    for m in script_re.finditer(text):
        refs.add(m.group(1))
    for m in link_css_re.finditer(text):
        refs.add(m.group(1))
    for m in font_re.finditer(text):
        refs.add(m.group(1))
    for r in refs:
        p = resolve(r, h.parent)
        if p and p.exists() and p.is_file():
            try:
                sz = p.stat().st_size
            except: continue
            ref_count[str(p)] += 1
            page_weight[str(h)] += sz
            page_imgs[str(h)].append((sz, str(p.relative_to(root.resolve())) if root.resolve() in p.parents or p == root.resolve() else str(p)))

print('=== TOP 20 HEAVIEST PAGES (sum of referenced assets) ===')
heavy_pages = sorted(page_weight.items(), key=lambda x:-x[1])[:20]
for pg, w in heavy_pages:
    print(f'{w/1024/1024:>7.2f} MB   {pg}')

print()
print('=== TOP 5 PAGES BREAKDOWN ===')
for pg, w in heavy_pages[:5]:
    print(f'\n--- {pg}  ({w/1024/1024:.2f} MB total) ---')
    items = sorted(page_imgs[pg], key=lambda x:-x[0])[:10]
    for sz, ref in items:
        print(f'  {sz/1024:>8.1f} KB  {ref}')

print()
print('=== TOP 25 HEAVIEST REFERENCED ASSETS (single file size) ===')
ref_sizes = []
for path_str, cnt in ref_count.items():
    p = Path(path_str)
    if p.exists():
        ref_sizes.append((p.stat().st_size, cnt, path_str))
ref_sizes.sort(key=lambda x:-x[0])
for sz, cnt, path_str in ref_sizes[:25]:
    try:
        rel = Path(path_str).relative_to(root.resolve())
    except:
        rel = path_str
    print(f'{sz/1024:>8.1f} KB  used on {cnt:>3} page(s)  {rel}')
