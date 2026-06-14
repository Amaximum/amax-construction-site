"""List blogs by format. Old = missing lede / key-takeaways / HowTo.

Service/location pages (Service or LocalBusiness schema without Article/
BlogPosting) are excluded so only real blog articles are classified.
"""
import re
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
    types = set(re.findall(r'"@type"\s*:\s*"([A-Za-z]+)"', text))
    is_blog = bool(types & {'Article', 'BlogPosting'})
    is_service = bool(types & {'Service', 'LocalBusiness'}) and not is_blog
    if is_service:
        # Service/location page, not a blog article — skip.
        continue
    has_lede = 'class="lede"' in text
    has_kt = 'key-takeaways' in text
    # NEW blogs carry the structured scaffold (lede + key-takeaways) plus a
    # rich schema type. HowTo is only appropriate for step-by-step posts;
    # pricing/selection/guide/cost posts correctly use FAQPage instead, so
    # either HowTo or FAQPage qualifies a blog as NEW format.
    has_rich_schema = '"HowTo"' in text or "'HowTo'" in text or '"FAQPage"' in text or "'FAQPage'" in text
    if has_lede and has_kt and has_rich_schema:
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
