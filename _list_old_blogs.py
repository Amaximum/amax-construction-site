"""List blogs by format. Old = missing lede / key-takeaways / HowTo."""
from pathlib import Path

root = Path('.')
old, new = [], []
SKIP = {'blog', 'locations', 'portfolio', 'services', 'css', 'js', 'img', '.git', '.venv', '__pycache__'}

for p in sorted(root.glob('*/index.html')):
    if p.parts[0] in SKIP:
        continue
    text = p.read_text(encoding='utf-8', errors='ignore')
    if 'class="blog-hero"' not in text:
        continue
    has_lede = 'class="lede"' in text
    has_kt = 'key-takeaways' in text
    has_howto = '"HowTo"' in text or "'HowTo'" in text
    if has_lede and has_kt and has_howto:
        new.append(p.parent.name)
    else:
        old.append(p.parent.name)

print(f'NEW format ({len(new)}):')
for s in new:
    print(f'  {s}')
print()
print(f'OLD format ({len(old)}):')
for s in old:
    print(f'  {s}')
